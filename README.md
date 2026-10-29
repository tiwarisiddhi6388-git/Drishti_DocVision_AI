# Drishti · DocVision AI

**Intelligent Document Structure Understanding**  
*From flat text → structured, traceable & decision-ready records*

Team **Trendline Titans** · Leader: Hariom Chandra Tripathi
                           , Member:- Siddhi Tiwari

---

## Overview

Drishti is a modular document AI pipeline that:

1. **Understands** – Advanced OCR (PaddleOCR PP-OCRv4) + layout classification  
2. **Structures** – reading order, label→value linking, table reconstruction  
3. **Decides** – schema checks, arithmetic reconciliation, confidence flags with evidence-linked review actions  

Every extracted value stays traceable to a source region. Low-confidence predictions are flagged, never guessed.

---

## Project Structure

```
drishti_docvision/
├── app.py                     # Streamlit frontend (dark/teal UX)
├── requirements.txt
├── Dockerfile                 # Multi-stage production image
├── docker-compose.yml
├── docker-entrypoint.sh
├── .dockerignore
├── .env.example
├── Makefile
├── frontend/
│   └── components.py
├── backend/
│   ├── pipeline.py            # 8-stage orchestrator
│   ├── preprocess.py
│   ├── structure.py
│   ├── extract.py
│   └── validate.py
├── ocr/
│   └── ocr_engine.py          # Advanced PaddleOCR + fallback mock
├── ml/
│   └── layout_analyzer.py
├── tests/
├── utils/
└── data/samples/
```

---

## Quick Start (Local)

```bash
cd drishti_docvision
pip install -r requirements.txt
streamlit run app.py
# or
make run
```

Open http://localhost:8501

The app **prefers real PaddleOCR**. If models cannot be downloaded it automatically falls back to a high-quality advanced mock so demos always work.

---

## Docker Deployment (Recommended)

### One-command start

```bash
docker compose up --build
```

Then open **http://localhost:8501**

### Useful commands

```bash
make docker-build   # build image
make docker-up      # start detached
make docker-down    # stop
```

### Environment

Copy `.env.example` → `.env` and adjust:

```bash
USE_REAL_OCR=1      # 1 = try PaddleOCR first
OCR_LANG=en
USE_GPU=0           # set 1 only with nvidia runtime
```

### Production notes

- Runs as non-root user `drishti`
- Health-check on `/_stcore/health`
- Volume mount `./data` for persistent uploads/samples
- Multi-stage build keeps the final image reasonably lean

---

## Advanced OCR

| Engine              | When used                          | Notes                          |
|---------------------|------------------------------------|--------------------------------|
| **PaddleOCR**       | Default when models available      | PP-OCRv4 + angle classification |
| **Advanced Mock**   | Fallback / CI / offline            | Deterministic, layout-aware    |

Toggle in the sidebar or control via `USE_REAL_OCR`.

---

## Pipeline Stages

| # | Stage       | What happens                              | Tool / Module          |
|---|-------------|-------------------------------------------|------------------------|
| 1 | Upload      | Accept PDF/PNG/JPEG, size & type checks   | Streamlit              |
| 2 | Preprocess  | Render, deskew, normalize                 | PyMuPDF + OpenCV       |
| 3 | OCR         | Words + boxes + confidence                | **PaddleOCR** / Mock   |
| 4 | Layout      | Heading / table / field / figure          | Layout analyzer        |
| 5 | Structure    | Reading order, label-value links          | Python                 |
| 6 | Extract     | Typed tables & key fields                 | Pydantic + pandas      |
| 7 | Validate    | Schema, arithmetic, confidence            | Custom rules           |
| 8 | Review      | Confirm / correct → JSON / CSV export     | Streamlit UI           |

---

## Tests

```bash
make test
# or
python tests/test_csv_store.py
python tests/test_validate.py
python tests/test_pipeline_smoke.py
```

## CSV Database

Each completed pipeline job is appended to CSV tables under `data/database/`.
The tables store document summaries, page metadata, OCR spans, layout regions,
extracted fields and key-values, table rows, and validation findings. The Export
tab provides downloads of these persistent CSV tables; each download includes
all jobs saved so far. Spreadsheet-formula-like text is escaped when written
to help keep OCR output safe to open in spreadsheet software.

---

## Responsible AI

- Public or permitted documents only  
- Uploads are session-scoped  
- Unknown / low-confidence values are flagged, never invented  
- Failures and mismatches are surfaced openly for human review  

---

Built with ❤️ by **Trendline Titans**
