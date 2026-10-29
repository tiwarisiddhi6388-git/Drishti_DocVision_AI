"""
Drishti DocVision AI
Intelligent Document Structure Understanding
Team: Trendline Titans
"""

from __future__ import annotations

import hashlib
import io
import sys
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.pipeline import run_pipeline
from frontend.components import (
    finding_card,
    inject_custom_css,
    region_badge,
    render_header,
)
from utils.helpers import safe_json_dumps

st.set_page_config(
    page_title="Drishti · DocVision AI",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()
render_header()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Pipeline Settings")
    use_real_ocr = st.toggle("Advanced OCR (PaddleOCR)", value=True,
                             help="Uses real PaddleOCR when available, otherwise advanced mock")
    deskew = st.toggle("Auto deskew", value=True)
    show_bboxes = st.toggle("Show region overlays", value=True)
    st.markdown("---")
    st.markdown("### 📋 About")
    st.markdown(
        """
**Drishti** turns document pages into inspectable structured records.

- Every value traces to a source region
- Low confidence is flagged, never guessed
- Arithmetic & schema checks for decision support
"""
    )
    st.markdown("---")
    st.caption("Leader: Hariom Chandra Tripathi  \nTeam Trendline Titans")

# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------
st.markdown('<div class="section-heading">Start a document review</div>', unsafe_allow_html=True)
with st.container(key="upload_panel"):
    uploaded = st.file_uploader(
        "Upload a document to begin",
        type=["pdf", "png", "jpg", "jpeg", "webp"],
        help="Public or permitted documents only. Uploads are processed in-session.",
    )

if uploaded is None:
    st.markdown(
        '<div class="section-heading">A clear path from page to decision</div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    stages = [
        ("01", "Read", "OCR captures text, position, and confidence."),
        ("02", "Understand", "Layout analysis groups content into regions."),
        ("03", "Structure", "Fields and tables become reviewable records."),
        ("04", "Validate", "Checks surface gaps and inconsistencies."),
    ]
    for col, (number, title, desc) in zip(cols, stages):
        with col:
            st.markdown(
                f"""
                <div class="card" style="min-height:145px;">
                    <div class="eyebrow">{number} / PROCESS</div>
                    <div style="font-size:1.04rem; font-weight:700; color:#edf7f3; margin-top:0.65rem;">{title}</div>
                    <div style="color:#9ab5ad; font-size:0.86rem; line-height:1.55; margin-top:0.45rem;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.caption("Supported: PDF, PNG, JPG, JPEG, WEBP · Documents are processed locally by this app.")
    st.stop()

# Save upload to temp
tmp_dir = ROOT / "data" / "tmp"
tmp_dir.mkdir(parents=True, exist_ok=True)
upload_bytes = uploaded.getvalue()
upload_key = hashlib.sha256(
    upload_bytes + f"{uploaded.name}:{use_real_ocr}:{deskew}".encode("utf-8")
).hexdigest()
tmp_path = tmp_dir / f"{upload_key[:16]}_{Path(uploaded.name).name}"
with open(tmp_path, "wb") as f:
    f.write(upload_bytes)

# ---------------------------------------------------------------------------
# Run pipeline
# ---------------------------------------------------------------------------
if st.session_state.get("pipeline_upload_key") == upload_key:
    result = st.session_state["pipeline_result"]
else:
    with st.spinner("Running Drishti pipeline… Preprocess → OCR → Layout → Structure → Validate"):
        try:
            result = run_pipeline(tmp_path, use_real_ocr=use_real_ocr, deskew=deskew)
        except Exception as e:
            st.error(f"Pipeline failed: {e}")
            st.stop()
    st.session_state["pipeline_upload_key"] = upload_key
    st.session_state["pipeline_result"] = result

st.markdown(
    f"""
    <div class="job-banner">
        <div>
            <div class="job-label">Current document</div>
            <div class="job-value">{Path(uploaded.name).name}</div>
        </div>
        <div style="display:flex; align-items:center; gap:0.75rem;">
            <div class="job-label">Job {result.job_id}</div>
            <span class="status-pill">● {result.status.title()}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Metrics row
# ---------------------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{len(result.pages)}</div>
            <div class="metric-label">Pages</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m2:
    n_regions = sum(len(p["regions"]) for p in result.pages)
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{n_regions}</div>
            <div class="metric-label">Regions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m3:
    conf = result.pages[0]["avg_ocr_confidence"] if result.pages else 0
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{conf:.0%}</div>
            <div class="metric-label">Avg OCR Conf</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with m4:
    score = result.validation.score if result.validation else 0
    color = "#6bcb77" if score >= 0.85 else "#ffd93d" if score >= 0.6 else "#ff6b6b"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{color};">{score:.0%}</div>
            <div class="metric-label">Decision Score</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_view, tab_structure, tab_validate, tab_export = st.tabs(
    ["📄 Document View", "🧩 Structure", "✅ Decision Support", "⬇️ Export"]
)

# ---- Document View ----
with tab_view:
    page = result.pages[0]
    img: Image.Image = page["image"].copy()

    if show_bboxes:
        draw = ImageDraw.Draw(img, "RGBA")
        colors = {
            "heading": (0, 224, 184, 90),
            "form_field": (180, 140, 255, 90),
            "table": (255, 210, 100, 90),
            "key_value": (100, 200, 255, 90),
            "figure": (160, 160, 160, 80),
        }
        for r in page["regions"]:
            c = colors.get(r.type, (0, 200, 150, 80))
            box = [int(v) for v in r.bbox]
            draw.rectangle(box, fill=c, outline=c[:3] + (220,), width=3)

    col_img, col_info = st.columns([1.4, 1])
    with col_img:
        st.image(img, caption=f"Page {page['page_num']} · overlays show detected regions", use_container_width=True)
    with col_info:
        st.markdown("#### Detected Regions")
        for r in page["regions"]:
            st.markdown(
                f"{region_badge(r.type)} **{r.text[:60]}{'…' if len(r.text)>60 else ''}**  \n"
                f"<small style='color:#8fb8ad'>conf {r.confidence:.2f} · bbox {[int(x) for x in r.bbox]}</small>",
                unsafe_allow_html=True,
            )
            st.markdown("")

# ---- Structure ----
with tab_structure:
    record = result.record
    if record is None:
        st.warning("No structured record produced.")
    else:
        st.markdown(f"#### Heading  \n**{record.heading or '—'}**")
        st.markdown("#### Key Fields")
        if record.fields:
            for f in record.fields:
                st.markdown(
                    f"- **{f.label}** → `{f.value}`  "
                    f"<small style='color:#8fb8ad'>(conf {f.confidence:.2f})</small>",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No form fields extracted.")

        st.markdown("#### Tables")
        if record.tables:
            import pandas as pd

            for i, t in enumerate(record.tables):
                df = pd.DataFrame(t.rows)
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.caption("No tables detected.")

        with st.expander("Raw region graph (JSON)"):
            st.code(safe_json_dumps(record.model_dump()), language="json")

# ---- Decision Support ----
with tab_validate:
    val = result.validation
    if val is None:
        st.info("No validation results.")
    else:
        status_icon = "✅" if val.is_valid else "⚠️"
        st.markdown(f"### {status_icon} Validation · score **{val.score:.0%}**")

        if not val.findings:
            st.success("No issues found. Document is ready for downstream use.")
        else:
            for f in val.findings:
                st.markdown(finding_card(f), unsafe_allow_html=True)

        st.markdown(
            """
            <div style="color:#8fb8ad; font-size:0.9rem; margin-top:1rem;">
            Code does the math. An inconsistency is a <strong>review prompt</strong>, not proof of fraud.
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---- Export ----
with tab_export:
    st.markdown("#### Download structured outputs")
    if result.record:
        json_str = safe_json_dumps(result.record.model_dump())
        st.download_button(
            "⬇️ Download JSON",
            data=json_str,
            file_name=f"drishti_{result.job_id}.json",
            mime="application/json",
        )

        # CSV for tables
        if result.record.tables:
            import pandas as pd

            df = pd.DataFrame(result.record.tables[0].rows)
            csv_buf = io.StringIO()
            df.to_csv(csv_buf, index=False)
            st.download_button(
                "⬇️ Download Table CSV",
                data=csv_buf.getvalue(),
                file_name=f"drishti_table_{result.job_id}.csv",
                mime="text/csv",
            )

    st.markdown("#### Persistent CSV database")
    st.caption(
        "Each completed job is appended to the CSV tables in data/database. "
        "These downloads contain records from all jobs stored so far."
    )
    for table_name, csv_path in result.csv_exports.items():
        path = Path(csv_path)
        if path.is_file():
            st.download_button(
                f"Download {table_name}",
                data=path.read_bytes(),
                file_name=path.name,
                mime="text/csv",
                key=f"database_{result.job_id}_{table_name}",
            )

    st.markdown("#### Pipeline timings (seconds)")
    for k, v in result.timings.items():
        st.caption(f"{k}: {v:.3f}s")

# Cleanup note
st.markdown("---")
st.caption(
    "Responsible AI · Public or permitted documents only · Uploads deleted after session · "
    "Unknown values flagged, never guessed"
)
