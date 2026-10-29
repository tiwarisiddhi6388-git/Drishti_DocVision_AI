"""Unit tests for validation rules."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.extract import DocumentRecord, FormField, TableRecord
from backend.validate import validate_document


def test_total_mismatch_detected():
    record = DocumentRecord(
        key_values={
            "Subtotal": "₹8,000",
            "Tax (18%)": "₹1,440",
            "Total Amount": "₹10,000",
        },
        fields=[
            FormField(label="Invoice No", value="INV-1", confidence=0.95),
            FormField(label="Date", value="12 Oct 2026", confidence=0.94),
        ],
    )
    result = validate_document(record)
    assert any(f.rule == "total_mismatch" for f in result.findings)
    assert result.is_valid is False


def test_happy_path():
    record = DocumentRecord(
        key_values={
            "Subtotal": "₹4,050",
            "Tax (18%)": "₹729",
            "Total Amount": "₹4,779",
        },
        fields=[
            FormField(label="Invoice No", value="INV-2048", confidence=0.96),
            FormField(label="Date", value="12 Oct 2026", confidence=0.95),
        ],
        tables=[
            TableRecord(
                headers=["Item", "Qty", "Unit Price", "Amount"],
                rows=[
                    {"Item": "USB hub", "Qty": "2", "Unit Price": "₹750", "Amount": "₹1,500"},
                    {"Item": "HDMI cable", "Qty": "3", "Unit Price": "₹450", "Amount": "₹1,350"},
                    {"Item": "Wireless mouse", "Qty": "1", "Unit Price": "₹1,200", "Amount": "₹1,200"},
                ],
            )
        ],
    )
    result = validate_document(record)
    assert result.is_valid is True
    assert result.score >= 0.9


def test_missing_required_field():
    record = DocumentRecord(key_values={"Total Amount": "₹100"})
    result = validate_document(record)
    assert any(f.rule == "required_field" for f in result.findings)


if __name__ == "__main__":
    test_total_mismatch_detected()
    test_happy_path()
    test_missing_required_field()
    print("All validation tests passed.")
