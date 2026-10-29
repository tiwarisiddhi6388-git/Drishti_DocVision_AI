.PHONY: help install run test docker-build docker-up docker-down clean

help:
	@echo "Drishti DocVision AI – common commands"
	@echo ""
	@echo "  make install       Install Python dependencies"
	@echo "  make run           Launch Streamlit locally"
	@echo "  make test          Run unit tests"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-up     Start with docker compose"
	@echo "  make docker-down   Stop containers"
	@echo "  make clean         Remove caches & temp files"

install:
	pip install -r requirements.txt

run:
	streamlit run app.py --server.port=8501

test:
	python tests/test_csv_store.py
	python tests/test_validate.py
	python tests/test_pipeline_smoke.py

docker-build:
	docker compose build

docker-up:
	docker compose up --build -d
	@echo "→ Open http://localhost:8501"

docker-down:
	docker compose down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf data/tmp/* .pytest_cache .mypy_cache 2>/dev/null || true
	@echo "Cleaned."
