"""
Advanced OCR engine for Drishti DocVision.

Primary engine : PaddleOCR (PP-OCRv4) with angle classification
Fallback       : High-quality deterministic mock for demos / CI
"""

from __future__ import annotations

import logging
import os
import random
from dataclasses import dataclass, field
from typing import List, Optional

from PIL import Image

logger = logging.getLogger(__name__)


@dataclass
class TextSpan:
    text: str
    bbox: List[float]  # [x1, y1, x2, y2]
    confidence: float
    page: int = 1


@dataclass
class OCRResult:
    spans: List[TextSpan] = field(default_factory=list)
    full_text: str = ""
    avg_confidence: float = 0.0
    engine: str = "unknown"


class BaseOCREngine:
    name: str = "base"

    def run(self, image: Image.Image, page_num: int = 1) -> OCRResult:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Advanced real engine – PaddleOCR
# ---------------------------------------------------------------------------
class PaddleOCREngine(BaseOCREngine):
    """
    Production-grade OCR using PaddleOCR (PP-OCRv4).
    Supports English + multilingual, angle classification, and high accuracy.
    """

    name = "paddleocr"

    def __init__(
        self,
        lang: str = "en",
        use_gpu: bool = False,
        use_angle_cls: bool = True,
        show_log: bool = False,
    ):
        try:
            from paddleocr import PaddleOCR
        except ImportError as e:
            raise ImportError(
                "PaddleOCR not installed. Run: pip install paddlepaddle paddleocr"
            ) from e

        # Disable model download progress spam in containers
        os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

        self.ocr = PaddleOCR(
            use_angle_cls=use_angle_cls,
            lang=lang,
            use_gpu=use_gpu,
            show_log=show_log,
            det_db_thresh=0.3,
            det_db_box_thresh=0.5,
            rec_batch_num=6,
        )
        logger.info("PaddleOCR engine initialised (lang=%s, gpu=%s)", lang, use_gpu)

    def run(self, image: Image.Image, page_num: int = 1) -> OCRResult:
        import numpy as np

        arr = np.array(image.convert("RGB"))
        raw = self.ocr.ocr(arr, cls=True)

        spans: List[TextSpan] = []
        if not raw or not raw[0]:
            return OCRResult(engine=self.name)

        for line in raw[0]:
            box, (text, conf) = line
            xs = [p[0] for p in box]
            ys = [p[1] for p in box]
            bbox = [float(min(xs)), float(min(ys)), float(max(xs)), float(max(ys))]
            spans.append(
                TextSpan(
                    text=text.strip(),
                    bbox=bbox,
                    confidence=float(conf),
                    page=page_num,
                )
            )

        full_text = " ".join(s.text for s in spans)
        avg = sum(s.confidence for s in spans) / max(len(spans), 1)
        return OCRResult(
            spans=spans,
            full_text=full_text,
            avg_confidence=avg,
            engine=self.name,
        )


# ---------------------------------------------------------------------------
# High-quality mock (used when real models are unavailable)
# ---------------------------------------------------------------------------
class AdvancedMockOCREngine(BaseOCREngine):
    """
    Deterministic, layout-aware mock that produces realistic invoice spans.
    Useful for demos, CI, and when PaddleOCR models cannot be downloaded.
    """

    name = "advanced_mock"

    def __init__(self, seed: Optional[int] = 42):
        self.rng = random.Random(seed)

    def run(self, image: Image.Image, page_num: int = 1) -> OCRResult:
        w, h = image.size
        spans: List[TextSpan] = []

        def conf(base: float = 0.94) -> float:
            return round(min(0.99, base + self.rng.uniform(-0.03, 0.04)), 3)

        # Company heading
        spans.append(TextSpan("NORTHSTAR SUPPLIES", [w * 0.08, h * 0.05, w * 0.52, h * 0.10], conf(0.97), page_num))
        spans.append(TextSpan("TAX INVOICE", [w * 0.68, h * 0.05, w * 0.90, h * 0.09], conf(0.96), page_num))

        # Form fields
        spans.append(TextSpan("Invoice No", [w * 0.08, h * 0.14, w * 0.22, h * 0.175], conf(), page_num))
        spans.append(TextSpan("INV-2048", [w * 0.24, h * 0.14, w * 0.38, h * 0.175], conf(0.98), page_num))
        spans.append(TextSpan("Date", [w * 0.08, h * 0.19, w * 0.15, h * 0.225], conf(), page_num))
        spans.append(TextSpan("12 Oct 2026", [w * 0.17, h * 0.19, w * 0.34, h * 0.225], conf(0.97), page_num))
        spans.append(TextSpan("GSTIN", [w * 0.08, h * 0.24, w * 0.16, h * 0.275], conf(), page_num))
        spans.append(TextSpan("29AABCT1332L1ZV", [w * 0.18, h * 0.24, w * 0.42, h * 0.275], conf(0.95), page_num))

        # Table header
        headers = ["Item", "HSN", "Qty", "Unit Price", "Amount"]
        col_x = [0.08, 0.32, 0.45, 0.55, 0.72]
        for txt, cx in zip(headers, col_x):
            spans.append(TextSpan(txt, [w * cx, h * 0.32, w * (cx + 0.10), h * 0.355], conf(0.96), page_num))

        # Table body
        rows = [
            ("USB hub 3.0", "8471", "2", "₹750", "₹1,500"),
            ("HDMI cable 2m", "8544", "3", "₹450", "₹1,350"),
            ("Wireless mouse", "8471", "1", "₹1,200", "₹1,200"),
        ]
        for r_idx, row in enumerate(rows):
            y0 = 0.37 + r_idx * 0.055
            for txt, cx in zip(row, col_x):
                spans.append(TextSpan(txt, [w * cx, h * y0, w * (cx + 0.10), h * (y0 + 0.04)], conf(), page_num))

        # Totals
        spans.append(TextSpan("Subtotal", [w * 0.55, h * 0.58, w * 0.68, h * 0.615], conf(), page_num))
        spans.append(TextSpan("₹4,050", [w * 0.72, h * 0.58, w * 0.88, h * 0.615], conf(0.98), page_num))
        spans.append(TextSpan("CGST @9%", [w * 0.55, h * 0.625, w * 0.68, h * 0.66], conf(), page_num))
        spans.append(TextSpan("₹364.50", [w * 0.72, h * 0.625, w * 0.88, h * 0.66], conf(), page_num))
        spans.append(TextSpan("SGST @9%", [w * 0.55, h * 0.67, w * 0.68, h * 0.705], conf(), page_num))
        spans.append(TextSpan("₹364.50", [w * 0.72, h * 0.67, w * 0.88, h * 0.705], conf(), page_num))
        spans.append(TextSpan("Total Amount", [w * 0.55, h * 0.73, w * 0.72, h * 0.77], conf(0.97), page_num))
        spans.append(TextSpan("₹4,779", [w * 0.74, h * 0.73, w * 0.90, h * 0.77], conf(0.99), page_num))

        full_text = " ".join(s.text for s in spans)
        avg = sum(s.confidence for s in spans) / max(len(spans), 1)
        return OCRResult(spans=spans, full_text=full_text, avg_confidence=avg, engine=self.name)


# ---------------------------------------------------------------------------
# Factory – prefers real advanced OCR
# ---------------------------------------------------------------------------
def get_ocr_engine(
    use_real: bool = True,
    lang: str = "en",
    use_gpu: bool = False,
) -> BaseOCREngine:
    """
    Return the best available OCR engine.
    When use_real=True (default), tries PaddleOCR first and falls back
    gracefully to the advanced mock if models cannot be loaded.
    """
    if use_real:
        try:
            engine = PaddleOCREngine(lang=lang, use_gpu=use_gpu)
            logger.info("Using advanced OCR engine: PaddleOCR")
            return engine
        except Exception as e:
            logger.warning("PaddleOCR unavailable (%s). Falling back to AdvancedMockOCR.", e)

    logger.info("Using AdvancedMockOCR engine")
    return AdvancedMockOCREngine(seed=42)
