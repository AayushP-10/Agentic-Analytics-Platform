.PHONY: install sample-data test lint backend frontend

install:
	python -m pip install -e ".[dev]"

sample-data:
	python scripts/generate_sample_data.py

test:
	python -m pytest

lint:
	python -m ruff check .

backend:
	python -m uvicorn backend.app.main:app --reload

frontend:
	python -m streamlit run frontend/streamlit_app.py
