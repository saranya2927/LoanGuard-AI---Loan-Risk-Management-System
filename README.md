# LoanGuard AI

A full-stack loan risk assessment system: applicants get an instant, explained
risk score; loan officers and admins get a portfolio dashboard and searchable
application history. Built around your team's real dataset and pipeline.

## Quick start

```bash
cd loanguard
python3 -m venv venv && source venv/bin/activate      # optional but recommended
pip install -r requirements.txt

# 1. Train the model (reproduces the Logistic Regression / Decision Tree /
#    Random Forest / XGBoost comparison and saves the best one)
python3 app/ml/train_model.py

# 2. Seed demo accounts + 180 historical applications from your dataset
python3 seed.py

# 3. Run the app (serves both the API and the frontend)
python -m uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000**. The `app/ml/loan_model.pkl` and `loanguard.db`
that ship in this folder are already trained/seeded, so you can skip steps 1-2
and go straight to `uvicorn app.main:app --reload` if you just want to see it
running.

### Demo accounts

| Role         | Email                    | Password        |
| ------------ | ------------------------ | --------------- |
| Applicant    | `applicant@loanguard.ai` | `Applicant@123` |
| Loan Officer | `officer@loanguard.ai`   | `Officer@123`   |
| Admin        | `admin@loanguard.ai`     | `Admin@123`     |

The login page also has one-click buttons to fill these in.

## What's actually working

- **Real model, not a mock.** `app/ml/train_model.py` trains Logistic
  Regression, Decision Tree, Random Forest, and XGBoost on
  `data/LoanGuard_AI_Final_Preprocessed_Dataset.csv`, picks the best by
  ROC-AUC, tunes it with a small grid search, and saves it. Current result:
  **Random Forest, 82.9% ROC-AUC, 80.0% accuracy** (see
  `app/ml/model_metrics.json` for the full report).
- **Real feature engineering.** `app/ml/predict.py` reproduces Saranya's
  pipeline (`Data_Engineer.ipynb`) server-side: DTI%, EMI-to-income,
  loan-to-income ratio, net worth, credit utilization category, etc. are all
  computed from the raw fields the applicant enters — the same
  transformations that produced the training CSV.
- **Real auth.** Session cookies signed with `itsdangerous`, passwords hashed
  with PBKDF2-HMAC-SHA256 (200k iterations), role-gated routes (`applicant`
  can only see their own applications; `officer`/`admin` see the full
  portfolio and dashboard).
- **Real database.** SQLite by default (zero setup). To switch to the
  PostgreSQL your team originally planned, just set `DATABASE_URL` before
  starting the app — nothing else changes:
  ```bash
  export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/loanguard"
  ```

## Fields the form doesn't ask for

A few columns in the training data aren't things an applicant would
naturally type into a form — they're the kind of thing a real underwriting
system derives internally. These are computed rather than collected:

- **`Interest_Rate_Percent`** — estimated from credit score (linear fit
  against the training data's actual credit-score/rate relationship).
- **`New_EMI`** — computed with the standard EMI formula from loan amount,
  tenure, and the estimated rate.
- **`Income_Stability_Score`** / **`Repayment_Consistency_Score`** — these
  were near-random in the source dataset (very weak correlation with any
  other column), so rather than reproduce noise, `predict.py` computes them
  from employment type/tenure and late-payment/default history with a
  simple, documented formula. See `estimate_income_stability` and
  `estimate_repayment_consistency` in `app/ml/predict.py` if you want to
  change the logic.

## Decision policy

Approve / Manual Review / Reject is a threshold on the model's predicted
default probability (`<25%` → Approve, `25-50%` → Manual Review, `≥50%` →
Reject) — set in `decide()` in `app/ml/predict.py`. This is a business rule,
not something the model outputs directly, so it's easy to change without
retraining.

One nuance: the **180 seeded historical applications carry the original
dataset's own `Risk_Level`/`Recommended_Decision` labels** (real historical
records), while anything you submit live goes through the current model +
policy above. So you may occasionally see a historical row where the labels
don't perfectly match today's thresholds — that's expected, not a bug.

## Project structure

```
loanguard/
  app/
    main.py              FastAPI app: routers + serves frontend/
    database.py           SQLAlchemy engine/session
    models.py              User, Application ORM models
    schemas.py              Pydantic request/response models
    auth.py                  Session cookies, password hashing, role gating
    ml/
      train_model.py         Trains & compares 4 models, saves the winner
      predict.py               Feature engineering + inference + decision policy
      loan_model.pkl            Trained pipeline (shipped, ready to use)
      model_metrics.json        Full evaluation report
    routers/
      auth.py                 /api/auth/*
      applications.py          /api/applications/* (submit, list, detail, CSV export)
      dashboard.py              /api/dashboard/summary
      demo.py                    /api/demo/predict (public, powers the landing page)
  data/
    LoanGuard_AI_Final_Preprocessed_Dataset.csv
  frontend/
    index.html, login.html, register.html,
    apply.html, result.html, dashboard.html, history.html
    css/, js/
  seed.py                  Demo accounts + historical data import
  requirements.txt
```

## Known gaps / next steps for the team

- `LoanGuard_AI_ML_Training.ipynb` came through as a Colab HTML export with
  empty/virtualized cells, so the model here was trained fresh from the CSV
  rather than reproducing your original notebook exactly. Re-export it
  properly (Colab: File → Download → Download .ipynb) if you want to compare.
- No PDF report export yet — CSV export is implemented
  (`/api/applications/{id}/export.csv`); PDF would be a good v2 addition.
- No password reset / email verification flow (out of scope for a class
  project demo).
- The interest-rate and derived-score formulas in `predict.py` are documented
  assumptions, not something specified in your original data dictionary —
  worth a quick team review before you present this.
