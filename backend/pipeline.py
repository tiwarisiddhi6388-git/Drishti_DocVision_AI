"""Main document understanding pipeline orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.csv_store import save_pipeline_result
from backend.extract import DocumentRecord, extract_records
from backend.preprocess import preprocess_document
from backend.structure import StructuredDocument, structure_page
from backend.validate import ValidationResult, validate_document
from ml.layout_analyzer import get_layout_analyzer
from ocr.ocr_engine import get_ocr_engine
from utils.helpers import generate_id, timestamp


@dataclass
class PipelineResult:
    job_id: str
    status: str
    pages: List[Dict[str, Any]] = field(default_factory=list)
    record: Optional[DocumentRecord] = None
    validation: Optional[ValidationResult] = None
    timings: Dict[str, float] = field(default_factory=dict)
    csv_exports: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=timestamp)


def run_pipeline(
    file_path: str | Path,
    use_real_ocr: bool = True,
    deskew: bool = True,
    database_dir: str | Path | None = None,
) -> PipelineResult:
    """
    Execute the full 8-stage pipeline:
    Upload → Preprocess → OCR → Layout → Structure → Extract → Validate → (Review)
    """
    import time

    job_id = generate_id()
    result = PipelineResult(job_id=job_id, status="running")
    timings = {}

    # Stage 2 – Preprocess
    t0 = time.time()
    pages = preprocess_document(file_path, deskew_enabled=deskew)
    timings["preprocess"] = time.time() - t0

    ocr_engine = get_ocr_engine(use_real=use_real_ocr)
    layout_engine = get_layout_analyzer(use_real=False)

    structured_docs: List[StructuredDocument] = []
    page_outputs = []

    for page in pages:
        page_num = page["page_num"]
        image = page["image"]

        # Stage 3 – OCR
        t0 = time.time()
        ocr_result = ocr_engine.run(image, page_num=page_num)
        timings[f"ocr_p{page_num}"] = time.time() - t0

        # Stage 4 – Layout
        t0 = time.time()
        layout_result = layout_engine.analyze(image, ocr_result.spans, page_num=page_num)
        timings[f"layout_p{page_num}"] = time.time() - t0

        # Stage 5 – Structure
        t0 = time.time()
        structured = structure_page(page_num, layout_result.regions, ocr_result.spans)
        timings[f"structure_p{page_num}"] = time.time() - t0
        structured_docs.append(structured)

        page_outputs.append(
            {
                "page_num": page_num,
                "width": page["width"],
                "height": page["height"],
                "skew_angle": page["skew_angle"],
                "image": image,
                "ocr_spans": ocr_result.spans,
                "regions": layout_result.regions,
                "avg_ocr_confidence": ocr_result.avg_confidence,
                "ocr_engine": ocr_result.engine,
            }
        )

    # Stage 6 – Extract
    t0 = time.time()
    record = extract_records(structured_docs)
    timings["extract"] = time.time() - t0

    # Stage 7 – Validate
    t0 = time.time()
    validation = validate_document(record)
    timings["validate"] = time.time() - t0

    result.pages = page_outputs
    result.record = record
    result.validation = validation
    result.timings = timings
    result.status = "completed"
    result.csv_exports = save_pipeline_result(
        result, Path(file_path).name, directory=database_dir
    )
    return result
