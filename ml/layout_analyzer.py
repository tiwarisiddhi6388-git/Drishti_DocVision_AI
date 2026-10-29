"""Layout analysis: classify regions (heading, table, form field, key-value, figure).

Mock implementation produces realistic regions that align with the MockOCREngine.
Real PP-StructureV3 can replace this later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from PIL import Image

from ocr.ocr_engine import TextSpan


@dataclass
class Region:
    type: str  # heading | paragraph | table | form_field | key_value | figure
    bbox: List[float]
    confidence: float
    text: str = ""
    page: int = 1
    children: List["Region"] = field(default_factory=list)
    meta: dict = field(default_factory=dict)


@dataclass
class LayoutResult:
    regions: List[Region] = field(default_factory=list)


class BaseLayoutAnalyzer:
    def analyze(
        self, image: Image.Image, ocr_spans: List[TextSpan], page_num: int = 1
    ) -> LayoutResult:
        raise NotImplementedError


class MockLayoutAnalyzer(BaseLayoutAnalyzer):
    """Heuristic layout grouping that works well with the mock OCR invoice."""

    def analyze(
        self, image: Image.Image, ocr_spans: List[TextSpan], page_num: int = 1
    ) -> LayoutResult:
        w, h = image.size
        regions: List[Region] = []

        # Group spans by approximate vertical bands
        heading_spans = [s for s in ocr_spans if s.bbox[1] < h * 0.13]
        field_spans = [s for s in ocr_spans if h * 0.13 <= s.bbox[1] < h * 0.28]
        table_spans = [s for s in ocr_spans if h * 0.28 <= s.bbox[1] < h * 0.55]
        kv_spans = [s for s in ocr_spans if s.bbox[1] >= h * 0.55]

        if heading_spans:
            xs = [s.bbox[0] for s in heading_spans] + [s.bbox[2] for s in heading_spans]
            ys = [s.bbox[1] for s in heading_spans] + [s.bbox[3] for s in heading_spans]
            text = " ".join(s.text for s in heading_spans)
            regions.append(
                Region(
                    type="heading",
                    bbox=[min(xs), min(ys), max(xs), max(ys)],
                    confidence=0.96,
                    text=text,
                    page=page_num,
                )
            )

        # Form fields – pair label + value
        labels = {"Invoice No", "Date", "Invoice"}
        for span in field_spans:
            if span.text in labels or "Invoice" in span.text:
                # find nearest value to the right
                value = None
                for other in field_spans:
                    if other is span:
                        continue
                    if other.bbox[0] > span.bbox[2] - 20 and abs(other.bbox[1] - span.bbox[1]) < 30:
                        value = other
                        break
                if value:
                    regions.append(
                        Region(
                            type="form_field",
                            bbox=[
                                min(span.bbox[0], value.bbox[0]),
                                min(span.bbox[1], value.bbox[1]),
                                max(span.bbox[2], value.bbox[2]),
                                max(span.bbox[3], value.bbox[3]),
                            ],
                            confidence=min(span.confidence, value.confidence),
                            text=f"{span.text} → {value.text}",
                            page=page_num,
                            meta={"label": span.text, "value": value.text},
                        )
                    )

        if table_spans:
            xs = [s.bbox[0] for s in table_spans] + [s.bbox[2] for s in table_spans]
            ys = [s.bbox[1] for s in table_spans] + [s.bbox[3] for s in table_spans]
            regions.append(
                Region(
                    type="table",
                    bbox=[min(xs) - 10, min(ys) - 5, max(xs) + 10, max(ys) + 5],
                    confidence=0.93,
                    text=" | ".join(s.text for s in table_spans[:4]),  # header hint
                    page=page_num,
                    meta={"n_spans": len(table_spans)},
                )
            )

        # Key-value pairs for totals
        for span in kv_spans:
            if any(k in span.text for k in ("Subtotal", "Tax", "Total")):
                value = None
                for other in kv_spans:
                    if other is span:
                        continue
                    if other.bbox[0] > span.bbox[2] - 30 and abs(other.bbox[1] - span.bbox[1]) < 25:
                        value = other
                        break
                if value:
                    regions.append(
                        Region(
                            type="key_value",
                            bbox=[
                                min(span.bbox[0], value.bbox[0]),
                                min(span.bbox[1], value.bbox[1]),
                                max(span.bbox[2], value.bbox[2]),
                                max(span.bbox[3], value.bbox[3]),
                            ],
                            confidence=min(span.confidence, value.confidence),
                            text=f"{span.text} → {value.text}",
                            page=page_num,
                            meta={"label": span.text, "value": value.text},
                        )
                    )

        # Dummy figure region (logo area)
        regions.append(
            Region(
                type="figure",
                bbox=[w * 0.75, h * 0.04, w * 0.95, h * 0.14],
                confidence=0.85,
                text="Company logo (no OCR text)",
                page=page_num,
            )
        )

        return LayoutResult(regions=regions)


def get_layout_analyzer(use_real: bool = False) -> BaseLayoutAnalyzer:
    # Real PP-StructureV3 would go here
    return MockLayoutAnalyzer()
