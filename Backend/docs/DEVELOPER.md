# Developer Guide

## Running locally

1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Run tests: `cd backend && pytest tests/ -v`

## Adding a new regex rule

Edit `backend/app/security/regex_detector.py` → `_rules()`.

## Enabling CodeBERT (after training)

1. Train with `colab/train_codebert.ipynb`
2. Extract model to `models/codebert-vuln/`
3. Implement `CodeBERTModel.load()` and `predict()` in `codebert_model.py`
4. Set `ML_PROVIDER=codebert` in `.env`

## Adding Semgrep custom config

Pass config path when constructing `SemgrepRunner(config="path/to/rules")` in analyzer.

## Frontend API URL

Set `VITE_API_URL=http://127.0.0.1:8000` in `frontend/.env` if not using Vite proxy.

## Code style

- Python 3.10+, type hints
- Pydantic v2 for API schemas
- Findings use `VulnerabilityFinding` dataclass throughout pipeline
