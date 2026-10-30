"""Reusable UI components and custom CSS for DrishtiDocVision."""

from __future__ import annotations

import streamlit as st


def inject_custom_css():
    st.markdown(
        """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-dark: #141414;
        --bg-card: #222222;
        --accent: #b83a35;
        --accent-soft: #dfb75d;
        --text-primary: #f2f0eb;
        --text-muted: #aaa69d;
        --danger: #e05b55;
        --warning: #dfb75d;
        --success: #9ac09d;
        --border: rgba(220, 214, 201, 0.14);
    }

    .stApp {
        background:
            radial-gradient(ellipse at 82% 0%, rgba(160, 49, 44, 0.13), transparent 34rem),
            linear-gradient(145deg, #151515 0%, #1b1b1b 48%, #111111 100%);
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMain"] > div { padding-top: 2rem; }
    [data-testid="stSidebar"] {
        background: rgba(17, 17, 17, 0.96);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] > div { padding-top: 1.8rem; }
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stCaptionContainer"] { color: var(--text-muted); }
    h1, h2, h3, h4 { letter-spacing: -0.035em; color: var(--text-primary); }

    /* Hide default Streamlit chrome a bit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .main-title {
        font-size: clamp(2.4rem, 5vw, 3.65rem);
        line-height: 1;
        font-weight: 800;
        background: linear-gradient(100deg, #f7f3ea 4%, #e8cb85 56%, #c69a43 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.065em;
        margin: 0.55rem 0 0.65rem;
    }

    .subtitle {
        color: #b7cbc4;
        font-size: 1.05rem;
        margin-bottom: 0.4rem;
        letter-spacing: -0.015em;
    }

    .eyebrow {
        color: #e0b95f;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }

    .hero-shell {
        position: relative;
        overflow: hidden;
        background: linear-gradient(112deg, rgba(43, 42, 40, 0.98), rgba(27, 27, 27, 0.94));
        border: 1px solid rgba(223, 183, 93, 0.24);
        border-radius: 22px;
        padding: clamp(1.35rem, 4vw, 2.5rem);
        margin: 0.7rem 0 1.4rem;
        box-shadow: 0 24px 70px rgba(0, 0, 0, 0.2);
    }
    .hero-shell:after {
        content: "";
        position: absolute;
        width: 18rem;
        height: 18rem;
        top: -11rem;
        right: -3rem;
        border: 1px solid rgba(223, 183, 93, 0.15);
        border-radius: 50%;
        box-shadow: 0 0 0 2rem rgba(223, 183, 93, 0.025),
                    0 0 0 4rem rgba(223, 183, 93, 0.02);
        pointer-events: none;
    }
    .hero-copy {
        max-width: 46rem;
        color: #c0bdb5;
        font-size: 0.98rem;
        line-height: 1.7;
        margin: 0;
    }

    .section-heading {
        color: #f0f8f4;
        font-size: 1.13rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin: 0.3rem 0 0.95rem;
    }

    .job-banner {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        background: rgba(35, 35, 35, 0.92);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.9rem 1.15rem;
        margin: 1rem 0 1.2rem;
    }
    .job-label { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; }
    .job-value { color: #eaf6f1; font-weight: 650; font-size: 0.92rem; margin-top: 0.2rem; }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.4rem 0.72rem;
        border-radius: 999px;
        background: rgba(223, 183, 93, 0.10);
        border: 1px solid rgba(223, 183, 93, 0.28);
        color: #e8c873;
        font-size: 0.78rem;
        font-weight: 650;
        white-space: nowrap;
    }

    .card {
        background: linear-gradient(145deg, rgba(40, 40, 39, 0.96), rgba(29, 29, 29, 0.98));
        border: 1px solid var(--border);
        border-radius: 17px;
        padding: 1.25rem 1.35rem;
        margin-bottom: 1rem;
        box-shadow: 0 12px 30px rgba(0,0,0,0.14);
    }

    .st-key-upload_panel {
        background: rgba(34, 34, 34, 0.82);
        border: 1px solid rgba(220, 214, 201, 0.17);
        border-radius: 18px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
    }
    .st-key-upload_panel [data-testid="stFileUploader"] {
        background: transparent;
        border: 0;
        padding: 0;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: #e5e3df !important;
        border: 1px dashed #a79f91 !important;
        border-radius: 13px !important;
        min-height: 150px;
    }
    [data-testid="stFileUploaderDropzone"] * {
        color: #34322f !important;
    }
    [data-testid="stFileUploaderDropzone"] button {
        color: #f4fbf8 !important;
        background: #a93430 !important;
        border: 0 !important;
        border-radius: 9px !important;
    }
    [data-testid="stFileUploaderDropzone"] button * {
        color: #f4fbf8 !important;
    }
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] label p,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] {
        color: #c4c0b8 !important;
    }

    .metric-card {
        position: relative;
        min-height: 112px;
        background: linear-gradient(145deg, rgba(43, 43, 42, 0.97), rgba(29, 29, 29, 0.98));
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1rem 1.15rem;
        text-align: left;
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.12);
        transition: transform 160ms ease, border-color 160ms ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(223, 183, 93, 0.42);
    }

    .metric-value {
        font-size: 2rem;
        line-height: 1.2;
        font-weight: 750;
        color: var(--accent-soft);
        margin-top: 0.45rem;
    }

    .metric-label {
        font-size: 0.72rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.11em;
        font-weight: 650;
    }

    .region-badge {
        display: inline-block;
        padding: 0.27rem 0.68rem;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 650;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }

    .badge-heading { background: #4a2926; color: #f0a29b; }
    .badge-form_field { background: #3a3430; color: #dec99c; }
    .badge-table { background: #514326; color: #f0d27e; }
    .badge-key_value { background: #353535; color: #dedbd4; }
    .badge-figure { background: #3a3a3a; color: #c0c0c0; }

    .finding-error {
        border-left: 4px solid var(--danger);
        background: rgba(184, 58, 53, 0.13);
        padding: 0.9rem 1.1rem;
        border-radius: 0 10px 10px 0;
        margin-bottom: 0.8rem;
    }
    .finding-warning {
        border-left: 4px solid var(--warning);
        background: rgba(223, 183, 93, 0.10);
        padding: 0.9rem 1.1rem;
        border-radius: 0 10px 10px 0;
        margin-bottom: 0.8rem;
    }
    .finding-info {
        border-left: 4px solid var(--accent);
        background: rgba(220, 214, 201, 0.06);
        padding: 0.9rem 1.1rem;
        border-radius: 0 10px 10px 0;
        margin-bottom: 0.8rem;
    }

    .stButton > button {
        background: linear-gradient(90deg, #bb4039, #92302c);
        color: #fff8f1;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.55rem 1.4rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(184, 58, 53, 0.30);
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #a93430, #dfb75d);
    }

    div[data-testid="stFileUploader"] {
        color: #edf7f3;
    }

    [data-testid="stTabs"] [role="tablist"] {
        gap: 0.35rem;
        border-bottom: 1px solid var(--border);
    }
    [data-testid="stTabs"] button[role="tab"] {
        color: #a7beb5;
        border-radius: 10px 10px 0 0;
        padding: 0.65rem 0.95rem;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #e5c46f;
        background: rgba(223, 183, 93, 0.08);
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }
    [data-testid="stExpander"] {
        background: rgba(35, 35, 35, 0.78);
        border: 1px solid var(--border);
        border-radius: 12px;
    }
    .stProgress > div {
        background: rgba(255,255,255,0.08);
    }
    .stDownloadButton > button {
        border: 1px solid rgba(223, 183, 93, 0.25);
        border-radius: 10px;
        background: rgba(43, 43, 42, 0.92);
        color: #f1e8d2;
    }
    .stDownloadButton > button:hover {
        border-color: #dfb75d;
        color: #dfb75d;
    }

    .json-box {
        background: #0a1814;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        overflow-x: auto;
    }
</style>
""",
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
        <div class="hero-shell">
            <div class="eyebrow">Document intelligence workspace</div>
            <div class="main-title">Drishti</div>
            <div class="subtitle">DocVision AI · Intelligent Document Structure Understanding</div>
            <p class="hero-copy">
                Turn scanned documents into structured, traceable records.
                Review every extracted value, inspect its source, and surface
                inconsistencies before data moves downstream.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def region_badge(rtype: str) -> str:
    cls = f"badge-{rtype}" if rtype in ("heading", "form_field", "table", "key_value", "figure") else "badge-heading"
    return f'<span class="region-badge {cls}">{rtype.upper().replace("_", " ")}</span>'


def finding_card(finding) -> str:
    cls = f"finding-{finding.severity}"
    return f"""
    <div class="{cls}">
        <strong>{finding.severity.upper()} · {finding.rule}</strong><br>
        {finding.message}<br>
        <small style="color:#8fb8ad">{finding.evidence}</small><br>
        <em>Next: {finding.next_action}</em>
    </div>
    """
