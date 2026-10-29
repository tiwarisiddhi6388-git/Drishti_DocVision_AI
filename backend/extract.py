"""Extraction: produce typed records from structured document."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field

from backend.structure import StructuredDocument


class FormField(BaseModel):
    label: str
    value: str
    confidence: float = 0.9
    bbox: List[float] = Field(default_factory=list)


class TableRecord(BaseModel):
    headers: List[str]
    rows: List[Dict[str, str]]
    bbox: List[float] = Field(default_factory=list)


class DocumentRecord(BaseModel):
    document_type: str = "invoice"
    heading: str = ""
    fields: List[FormField] = Field(default_factory=list)
    tables: List[TableRecord] = Field(default_factory=list)
    key_values: Dict[str, str] = Field(default_factory=dict)
    raw_regions: List[Dict[str, Any]] = Field(default_factory=list)
    page_count: int = 1


def extract_records(docs: List[StructuredDocument]) -> DocumentRecord:
    if not docs:
        return DocumentRecord()

    heading = ""
    fields: List[FormField] = []
    tables: List[TableRecord] = []
    all_kv: Dict[str, str] = {}
    raw_regions = []

    for doc in docs:
        for r in doc.regions:
            raw_regions.append(
                {
                    "type": r.type,
                    "text": r.text,
                    "bbox": r.bbox,
                    "confidence": r.confidence,
                    "page": r.page,
                    "meta": r.meta,
                }
            )
            if r.type == "heading" and not heading:
                heading = r.text
            if r.type in ("form_field", "key_value") and r.meta:
                fields.append(
                    FormField(
                        label=r.meta.get("label", ""),
                        value=r.meta.get("value", ""),
                        confidence=r.confidence,
                        bbox=r.bbox,
                    )
                )
        all_kv.update(doc.key_values)
        for t in doc.tables:
            tables.append(
                TableRecord(
                    headers=t.get("headers", []),
                    rows=t.get("rows", []),
                    bbox=t.get("bbox", []),
                )
            )

    return DocumentRecord(
        heading=heading,
        fields=fields,
        tables=tables,
        key_values=all_kv,
        raw_regions=raw_regions,
        page_count=len(docs),
    )
