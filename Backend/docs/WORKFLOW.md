# Local PC + Google Colab Workflow

Training CodeBERT on **DetectVul/devign** (~27k samples) requires a GPU. With `CUDA available: False` on your PC, use this split:

| Where | What | GPU needed? |
|-------|------|-------------|
| **Local PC** | Code, dataset inspect, RAG, API, Streamlit, inference tests | No |
| **Google Colab T4** | `src/train.py` + `src/evaluate.py` | Yes (~3–5 hrs) |

Dataset is downloaded automatically from Hugging Face — **no CSV, no train.json**.

---

## Phase 1 — Local PC (development)

### 1. Install & verify

```powershell
cd c:\Users\GUEST-1\ai-code-reviewer
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts\verify_local_dev.py
```

### 2. Inspect Hugging Face dataset

```powershell
python scripts\inspect_dataset.py
```

Shows train / validation / test counts, class balance, and a sample `func` snippet.

### 3. Build RAG locally

```powershell
python src\ingest.py --seed-only
```

### 4. Develop without a trained model

Until Colab finishes, the app uses base CodeBERT weights. You can still test RAG, API, and UI:

```powershell
streamlit run app\streamlit_app.py
uvicorn api.main:app --reload
```

### 5. Optional local smoke test (CPU, ~200 samples)

```powershell
python src\train.py --allow-cpu --max-samples 200 --epochs 1
```

---

## Phase 2 — Google Colab (training only)

### 1. Open the notebook

`colab/train_codebert.ipynb` → **Runtime → Change runtime type → T4 GPU**

### 2. Get project code on Colab

- Set `REPO_URL` and clone, **or**
- Upload a zip of your `ai-code-reviewer` project folder (code only — not a dataset file)

### 3. Train + evaluate

The notebook runs:

```bash
python scripts/inspect_dataset.py   # auto-downloads DetectVul/devign
python src/train.py --output models/codebert-vuln --epochs 3 --batch-size 16 --lr 2e-5
python src/evaluate.py --model models/codebert-vuln --output results/metrics.json
```

### 4. Download artifacts

- `codebert-vuln.zip` → extract to `models/codebert-vuln/`
- `metrics.json` → `results/metrics.json`

---

## Phase 3 — Local PC (use trained model)

```powershell
python scripts\verify_local_dev.py
streamlit run app\streamlit_app.py
```

---

## Workflow diagram

```
Hugging Face DetectVul/devign
        ↓
   src/train.py  (Colab T4)
        ↓
 models/codebert-vuln/
        ↓
  Local inference + Streamlit
```

---

## What NOT to run locally

| Command | On CPU-only PC |
|---------|----------------|
| `python src/train.py` (full dataset) | **Blocked** — use Colab |
| `python src/train.py --allow-cpu --max-samples 200` | OK for smoke test |
| `python src/evaluate.py` | OK after training (slower on CPU) |
| `python scripts/inspect_dataset.py` | OK — downloads metadata only |

---

## Troubleshooting

**`CUDA available: False` when running train.py**  
Expected on a laptop without GPU. Use Colab.

**Hugging Face download slow**  
Set `HF_TOKEN` in environment for higher rate limits.

**Model not found in Streamlit**  
Extract `codebert-vuln.zip` so `models/codebert-vuln/config.json` exists.
