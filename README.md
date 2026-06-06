# vegil.dev

## AI Security Code Review Platform

Student-project Application Security Testing platform combining static analysis (Regex, Semgrep, Bandit) with pluggable ML risk scoring (mock heuristics now, CodeBERT later).

## Architecture

```
Source Code → Regex → Semgrep → Bandit → ML (mock/CodeBERT) → Risk Engine → Explainer → Report
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/API.md](docs/API.md).

## Quick start

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 (proxies `/api` → backend).

### Tests

```powershell
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

## ML providers

| Provider | Env | Description |
|----------|-----|-------------|
| `mock` (default) | `ML_PROVIDER=mock` | Heuristic risk — works without GPU |
| `codebert` | `ML_PROVIDER=codebert` | Implement `backend/app/ml/codebert_model.py` after training |

Train CodeBERT: [colab/train_codebert.ipynb](colab/train_codebert.ipynb) → extract to `models/codebert-vuln/`.

## Optional scanners

```powershell
pip install semgrep bandit
```

Scanners are skipped gracefully if not installed.

## Project layout

```
backend/app/     FastAPI, security engines, ML abstraction
frontend/        React + TypeScript + Tailwind + Monaco
colab/           CodeBERT training notebook
docs/            Architecture, API, developer guide
data/reports/    Saved analysis reports
models/          Fine-tuned CodeBERT (after training)
```

## Environment

Copy `.env.example` to `.env`:

```
ML_PROVIDER=mock
CODEBERT_MODEL_PATH=models/codebert-vuln
CORS_ORIGINS=http://localhost:5173
```

## License

Educational / student project.
