"""Smoke test for the full pipeline using a generated synthetic image."""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.pipeline import run_pipeline


def _make_dummy_invoice(path: Path):
    img = Image.new("RGB", (800, 1100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 760, 1060], outline=(30, 30, 30), width=2)
    draw.text((60, 70), "NORTHSTAR SUPPLIES", fill=(0, 0, 0))
    draw.text((60, 160), "Invoice No  INV-2048", fill=(0, 0, 0))
    draw.text((60, 210), "Date  12 Oct 2026", fill=(0, 0, 0))
    draw.text((60, 320), "Item          Qty   Unit Price   Amount", fill=(0, 0, 0))
    draw.text((60, 370), "USB hub       2     750          1500", fill=(0, 0, 0))
    draw.text((60, 700), "Total Amount  4779", fill=(0, 0, 0))
    img.save(path)


def test_pipeline_runs():
    tmp = ROOT / "data" / "tmp" / "smoke_invoice.png"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    _make_dummy_invoice(tmp)

    result = run_pipeline(
        tmp,
        use_real_ocr=False,
        deskew=False,
        database_dir=tmp.parent / "database",
    )
    assert result.status == "completed"
    assert result.record is not None
    assert result.validation is not None
    assert len(result.pages) == 1
    assert "documents.csv" in result.csv_exports
    assert "ocr_spans.csv" in result.csv_exports
    assert "regions.csv" in result.csv_exports
    assert Path(result.csv_exports["documents.csv"]).is_file()
    print("Pipeline smoke test passed. Job:", result.job_id)


if __name__ == "__main__":
    test_pipeline_runs()
