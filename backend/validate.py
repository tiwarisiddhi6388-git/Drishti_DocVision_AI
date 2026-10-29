"""Validation & decision support: schema, arithmetic, confidence checks."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from backend.extract import DocumentRecord


@dataclass
class Finding:
    severity: str  # info | warning | error
    rule: str
    message: str
    evidence: str
    next_action: str
    related_fields: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    findings: List[Finding] = field(default_factory=list)
    is_valid: bool = True
    score: float = 1.0


def _parse_amount(text: str) -> Optional[float]:
    if not text:
        return None
    # Remove currency symbols and commas
    cleaned = re.sub(r"[₹$€£,\s]", "", text)
    try:
        return float(cleaned)
    except ValueError:
        return None


def validate_document(record: DocumentRecord) -> ValidationResult:
    findings: List[Finding] = []

    # 1. Required fields
    required = ["Invoice No", "Date"]
    present_labels = {f.label for f in record.fields} | set(record.key_values.keys())
    for req in required:
        if req not in present_labels:
            findings.append(
                Finding(
                    severity="warning",
                    rule="required_field",
                    message=f"Missing required field: {req}",
                    evidence="Field not found in extracted key-value pairs.",
                    next_action="Check the original document or correct OCR region.",
                    related_fields=[req],
                )
            )

    # 2. Arithmetic consistency on totals
    kv = record.key_values
    subtotal = _parse_amount(kv.get("Subtotal", ""))
    tax = _parse_amount(kv.get("Tax (18%)", "") or kv.get("Tax", ""))
    total = _parse_amount(kv.get("Total Amount", "") or kv.get("Total", ""))

    if subtotal is not None and tax is not None and total is not None:
        expected = round(subtotal + tax, 2)
        if abs(expected - total) > 1.0:  # allow small rounding
            findings.append(
                Finding(
                    severity="error",
                    rule="total_mismatch",
                    message="Line items / tax do not reconcile with the stated total.",
                    evidence=(
                        f"Subtotal ₹{subtotal:,.2f} + Tax ₹{tax:,.2f} "
                        f"= ₹{expected:,.2f} but stated total is ₹{total:,.2f} "
                        f"(difference ₹{abs(expected - total):,.2f})"
                    ),
                    next_action=(
                        "Verify the original invoice, check omitted charges or "
                        "OCR errors, and confirm the corrected total before approval."
                    ),
                    related_fields=["Subtotal", "Tax", "Total Amount"],
                )
            )

    # 3. Table row sum vs Subtotal
    if record.tables:
        table = record.tables[0]
        amounts = []
        for row in table.rows:
            amt = _parse_amount(row.get("Amount", ""))
            if amt is not None:
                amounts.append(amt)
        if amounts and subtotal is not None:
            row_sum = sum(amounts)
            if abs(row_sum - subtotal) > 1.0:
                findings.append(
                    Finding(
                        severity="warning",
                        rule="table_sum_mismatch",
                        message="Sum of line-item amounts does not match Subtotal.",
                        evidence=f"Row sum = ₹{row_sum:,.2f}, Subtotal = ₹{subtotal:,.2f}",
                        next_action="Re-examine table cells and Subtotal region.",
                        related_fields=["Amount", "Subtotal"],
                    )
                )

    # 4. Low confidence flags
    for f in record.fields:
        if f.confidence < 0.90:
            findings.append(
                Finding(
                    severity="info",
                    rule="low_confidence",
                    message=f"Low confidence extraction for '{f.label}'",
                    evidence=f"Confidence score: {f.confidence:.2f}",
                    next_action="Human review recommended for this field.",
                    related_fields=[f.label],
                )
            )

    is_valid = not any(f.severity == "error" for f in findings)
    score = 1.0 - 0.15 * len([f for f in findings if f.severity == "error"])
    score = max(0.0, min(1.0, score - 0.05 * len([f for f in findings if f.severity == "warning"])))

    return ValidationResult(findings=findings, is_valid=is_valid, score=round(score, 3))
