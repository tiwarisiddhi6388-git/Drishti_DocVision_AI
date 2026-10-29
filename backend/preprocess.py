"""Document preprocessing: render pages, deskew, normalize."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
from PIL import Image

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # type: ignore


def render_pdf_pages(pdf_path: str | Path, dpi: int = 200) -> List[Image.Image]:
    """Render each page of a PDF to a high-quality PIL Image."""
    doc = fitz.open(str(pdf_path))
    pages: List[Image.Image] = []
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    for page in doc:
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        pages.append(img)
    doc.close()
    return pages


def load_image(path: str | Path) -> Image.Image:
    """Load a single image file."""
    return Image.open(path).convert("RGB")


def deskew(image: np.ndarray) -> Tuple[np.ndarray, float]:
    """Estimate and correct skew angle. Returns corrected image and angle used."""
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY) if image.ndim == 3 else image
    gray = cv2.bitwise_not(gray)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    coords = np.column_stack(np.where(thresh > 0))
    if len(coords) < 100:
        return image, 0.0

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Only correct significant skew
    if abs(angle) < 0.5:
        return image, 0.0

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated, float(angle)


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Basic contrast / brightness normalization."""
    lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)


def preprocess_document(
    file_path: str | Path, deskew_enabled: bool = True
) -> List[dict]:
    """
    Full preprocess pipeline.
    Returns list of page dicts: {page_num, image (PIL), width, height, skew_angle}
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        pages = render_pdf_pages(path)
    elif suffix in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}:
        pages = [load_image(path)]
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    results = []
    for i, pil_img in enumerate(pages):
        arr = np.array(pil_img)
        skew = 0.0
        if deskew_enabled:
            arr, skew = deskew(arr)
        arr = normalize_image(arr)
        final = Image.fromarray(arr)
        results.append(
            {
                "page_num": i + 1,
                "image": final,
                "width": final.width,
                "height": final.height,
                "skew_angle": skew,
            }
        )
    return results
