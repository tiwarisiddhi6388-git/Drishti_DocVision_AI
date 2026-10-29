"""Tests for persistent CSV storage."""

import csv
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.csv_store import save_pipeline_result


def test_pipeline_result_is_saved_to_csv_tables():
    region = SimpleNamespace(
        type="form_field",
        text="Invoice No → =SUM(1,1)",
        bbox=[1, 2, 3, 4],
        confidence=0.95,
        meta={"label": "Invoice No", "value": "=SUM(1,1)"},
    )
    span = SimpleNamespace(
        text="=SUM(1,1)", bbox=[1, 2, 3, 4], confidence=0.95
    )
    field = SimpleNamespace(
        label="Invoice No",
        value="=SUM(1,1)",
        confidence=0.95,
        bbox=[1, 2, 3, 4],
    )
    table = SimpleNamespace(
        headers=["Item", "Amount"],
        rows=[{"Item": "Cable", "Amount": "$12"}],
        bbox=[1, 2, 3, 4],
    )
    finding = SimpleNamespace(
        severity="warning",
        rule="required_field",
        message="Missing date",
        evidence="Date was not found.",
        next_action="Review document.",
        related_fields=["Date"],
    )
    result = SimpleNamespace(
        job_id="test-job",
        created_at="2026-10-27 12:00:00 UTC",
        status="completed",
        record=SimpleNamespace(
            document_type="invoice",
            heading="Invoice",
            page_count=1,
            fields=[field],
            key_values={"Invoice No": "=SUM(1,1)"},
            tables=[table],
        ),
        validation=SimpleNamespace(
            is_valid=True, score=0.95, findings=[finding]
        ),
        pages=[
            {
                "page_num": 1,
                "width": 100,
                "height": 200,
                "skew_angle": 0.0,
                "avg_ocr_confidence": 0.95,
                "ocr_engine": "advanced_mock",
                "ocr_spans": [span],
                "regions": [region],
            }
        ],
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        paths = save_pipeline_result(result, "invoice.png", temp_dir)
        save_pipeline_result(result, "invoice.png", temp_dir)
        expected_tables = {
            "documents.csv",
            "pages.csv",
            "ocr_spans.csv",
            "regions.csv",
            "fields.csv",
            "key_values.csv",
            "tables.csv",
            "table_rows.csv",
            "findings.csv",
        }
        assert set(paths) == expected_tables
        assert all(Path(path).is_file() for path in paths.values())

        with Path(paths["fields.csv"]).open(newline="", encoding="utf-8") as file:
            saved_fields = list(csv.DictReader(file))
        assert len(saved_fields) == 2
        saved_field = saved_fields[0]
        assert saved_field["value"] == "'=SUM(1,1)"

        with Path(paths["ocr_spans.csv"]).open(
            newline="", encoding="utf-8"
        ) as file:
            saved_span = next(csv.DictReader(file))
        assert saved_span["text"] == "'=SUM(1,1)"


if __name__ == "__main__":
    test_pipeline_result_is_saved_to_csv_tables()
    print("CSV store test passed.")
