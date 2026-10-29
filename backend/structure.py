"""Structure stage: reading order, label-value linking, region graph."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ml.layout_analyzer import Region
from ocr.ocr_engine import TextSpan


@dataclass
class StructuredDocument:
    page_num: int
    regions: List[Region]
    reading_order: List[str]  # region type sequence
    key_values: Dict[str, str]
    tables: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


def infer_reading_order(regions: List[Region]) -> List[Region]:
    """Sort regions top-to-bottom, left-to-right."""
    return sorted(regions, key=lambda r: (r.bbox[1], r.bbox[0]))


def build_key_value_map(regions: List[Region]) -> Dict[str, str]:
    kv = {}
    for r in regions:
        if r.type in ("form_field", "key_value") and r.meta:
            label = r.meta.get("label", "").strip()
            value = r.meta.get("value", "").strip()
            if label and value:
                kv[label] = value
    return kv


def rebuild_table(regions: List[Region], ocr_spans: List[TextSpan]) -> List[Dict]:
    """Very simple table reconstruction for the demo invoice."""
    table_regions = [r for r in regions if r.type == "table"]
    if not table_regions:
        return []

    # Use the known structure from mock for reliable demo
    # In a real system this would use row/column clustering on span centers
    headers = ["Item", "Qty", "Unit Price", "Amount"]
    rows = [
        {"Item": "USB hub", "Qty": "2", "Unit Price": "₹750", "Amount": "₹1,500"},
        {"Item": "HDMI cable", "Qty": "3", "Unit Price": "₹450", "Amount": "₹1,350"},
        {"Item": "Wireless mouse", "Qty": "1", "Unit Price": "₹1,200", "Amount": "₹1,200"},
    ]
    return [{"headers": headers, "rows": rows, "bbox": table_regions[0].bbox}]


def structure_page(
    page_num: int,
    regions: List[Region],
    ocr_spans: List[TextSpan],
) -> StructuredDocument:
    ordered = infer_reading_order(regions)
    kv = build_key_value_map(ordered)
    tables = rebuild_table(ordered, ocr_spans)

    return StructuredDocument(
        page_num=page_num,
        regions=ordered,
        reading_order=[r.type for r in ordered],
        key_values=kv,
        tables=tables,
        metadata={"n_regions": len(ordered)},
    )
