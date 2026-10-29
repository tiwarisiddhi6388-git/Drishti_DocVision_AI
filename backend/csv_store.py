"""Persistent CSV storage for document-processing results."""

from __future__ import annotations

import csv
import json
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.pipeline import PipelineResult


_WRITE_LOCK = threading.Lock()
_TABLE_HEADERS = {
    "documents.csv": (
        "job_id",
        "created_at",
        "file_name",
        "status",
        "document_type",
        "heading",
        "page_count",
        "is_valid",
        "validation_score",
    ),
    "pages.csv": (
        "job_id",
        "page_num",
        "width",
        "height",
        "skew_angle",
        "avg_ocr_confidence",
        "ocr_engine",
    ),
    "ocr_spans.csv": (
        "job_id",
        "page_num",
        "span_index",
        "text",
        "bbox",
        "confidence",
    ),
    "regions.csv": (
        "job_id",
        "page_num",
        "region_index",
        "type",
        "text",
        "bbox",
        "confidence",
        "meta",
    ),
    "fields.csv": ("job_id", "label", "value", "confidence", "bbox"),
    "key_values.csv": ("job_id", "label", "value"),
    "tables.csv": ("job_id", "table_index", "headers", "bbox"),
    "table_rows.csv": ("job_id", "table_index", "row_index", "values"),
    "findings.csv": (
        "job_id",
        "finding_index",
        "severity",
        "rule",
        "message",
        "evidence",
        "next_action",
        "related_fields",
    ),
}


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def _spreadsheet_safe(value: Any) -> Any:
    """Prevent text values from being interpreted as spreadsheet formulas."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def _append_rows(directory: Path, table_name: str, rows: list[dict[str, Any]]) -> Path:
    path = directory / table_name
    if not rows:
        return path

    directory.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=_TABLE_HEADERS[table_name])
        if write_header:
            writer.writeheader()
        for row in rows:
            writer.writerow({key: _spreadsheet_safe(value) for key, value in row.items()})
    return path


def save_pipeline_result(
    result: PipelineResult,
    file_name: str,
    directory: str | Path | None = None,
) -> dict[str, str]:
    """Append a completed pipeline result to the CSV database tables."""
    output_dir = (
        Path(directory)
        if directory is not None
        else Path(__file__).resolve().parents[1] / "data" / "database"
    )
    job_id = result.job_id
    record = result.record

    rows_by_table: dict[str, list[dict[str, Any]]] = {
        table_name: [] for table_name in _TABLE_HEADERS
    }
    rows_by_table["documents.csv"].append(
        {
            "job_id": job_id,
            "created_at": result.created_at,
            "file_name": Path(file_name).name,
            "status": result.status,
            "document_type": record.document_type if record else "",
            "heading": record.heading if record else "",
            "page_count": record.page_count if record else 0,
            "is_valid": result.validation.is_valid if result.validation else "",
            "validation_score": result.validation.score if result.validation else "",
        }
    )

    for page in result.pages:
        page_num = page["page_num"]
        rows_by_table["pages.csv"].append(
            {
                "job_id": job_id,
                "page_num": page_num,
                "width": page["width"],
                "height": page["height"],
                "skew_angle": page["skew_angle"],
                "avg_ocr_confidence": page["avg_ocr_confidence"],
                "ocr_engine": page["ocr_engine"],
            }
        )
        for index, span in enumerate(page["ocr_spans"]):
            rows_by_table["ocr_spans.csv"].append(
                {
                    "job_id": job_id,
                    "page_num": page_num,
                    "span_index": index,
                    "text": span.text,
                    "bbox": _json(span.bbox),
                    "confidence": span.confidence,
                }
            )
        for index, region in enumerate(page["regions"]):
            rows_by_table["regions.csv"].append(
                {
                    "job_id": job_id,
                    "page_num": page_num,
                    "region_index": index,
                    "type": region.type,
                    "text": region.text,
                    "bbox": _json(region.bbox),
                    "confidence": region.confidence,
                    "meta": _json(region.meta),
                }
            )

    if record:
        for field in record.fields:
            rows_by_table["fields.csv"].append(
                {
                    "job_id": job_id,
                    "label": field.label,
                    "value": field.value,
                    "confidence": field.confidence,
                    "bbox": _json(field.bbox),
                }
            )
        for label, value in record.key_values.items():
            rows_by_table["key_values.csv"].append(
                {"job_id": job_id, "label": label, "value": value}
            )
        for table_index, table in enumerate(record.tables):
            rows_by_table["tables.csv"].append(
                {
                    "job_id": job_id,
                    "table_index": table_index,
                    "headers": _json(table.headers),
                    "bbox": _json(table.bbox),
                }
            )
            for row_index, values in enumerate(table.rows):
                rows_by_table["table_rows.csv"].append(
                    {
                        "job_id": job_id,
                        "table_index": table_index,
                        "row_index": row_index,
                        "values": _json(values),
                    }
                )

    if result.validation:
        for index, finding in enumerate(result.validation.findings):
            rows_by_table["findings.csv"].append(
                {
                    "job_id": job_id,
                    "finding_index": index,
                    "severity": finding.severity,
                    "rule": finding.rule,
                    "message": finding.message,
                    "evidence": finding.evidence,
                    "next_action": finding.next_action,
                    "related_fields": _json(finding.related_fields),
                }
            )

    with _WRITE_LOCK:
        paths = {
            table_name: str(_append_rows(output_dir, table_name, rows))
            for table_name, rows in rows_by_table.items()
        }
    return paths
