"""
LoanGuard AI - Model training script
-------------------------------------
Reproduces the team's planned workflow (per __Loan_Risk_Assessment_System_Roles___Data.docx):
train Logistic Regression, Decision Tree, Random Forest and XGBoost, compare them,
tune the winner, and save the best pipeline as loan_model.pkl.

Input: LoanGuard_AI_Final_Preprocessed_Dataset.csv (Saranya's cleaned + feature-engineered
dataset - already has missing values handled, duplicates removed, outliers capped, and the
engineered ratio/burden columns added).

Run:
    python3 app/ml/train_model.py
"""
import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent.parent / "data" / "LoanGuard_AI_Final_Preprocessed_Dataset.csv"
MODEL_PATH = BASE_DIR / "loan_model.pkl"
METRICS_PATH = BASE_DIR / "model_metrics.json"

# Columns that are outputs / identifiers, not applicant-known-at-prediction-time inputs.
# (Same exclusion list Saranya used in Data_Engineer.ipynb, plus Application_Status which
# is a workflow status rather than an applicant attribute.)
LEAK_COLUMNS = [
    "Applicant_ID",
    "Name",
    "Risk_Score",
    "Risk_Level",
    "Recommended_Decision",
    "Default_Probability_Percent",
    "Loan_Status",
    "Application_Status",
]
TARGET = "Default_Flag"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    return df


def build_pipeline(numeric_features, categorical_features, estimator) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )
    return Pipeline(steps=[("preprocessor", preprocessor), ("model", estimator)])


def main():
    df = load_data()
    X = df.drop(columns=LEAK_COLUMNS + [TARGET])
    y = df[TARGET]

    numeric_features = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = X.select_dtypes(include=["object", "category"]).columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    candidates = {
        "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=6, class_weight="balanced"),
        "Random Forest": RandomForestClassifier(
            random_state=42, n_estimators=300, max_depth=10, class_weight="balanced"
        ),
        "XGBoost": XGBClassifier(
            random_state=42,
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            eval_metric="logloss",
            scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
        ),
    }

    results = {}
    fitted_pipelines = {}

    for name, estimator in candidates.items():
        pipe = build_pipeline(numeric_features, categorical_features, estimator)
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)
        proba = pipe.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, preds)
        f1 = f1_score(y_test, preds)
        auc = roc_auc_score(y_test, proba)

        results[name] = {"accuracy": acc, "f1": f1, "roc_auc": auc}
        fitted_pipelines[name] = pipe

        print(f"\n== {name} ==")
        print(f"Accuracy: {acc:.4f}  F1: {f1:.4f}  ROC-AUC: {auc:.4f}")
        print(classification_report(y_test, preds, target_names=["No Default", "Default"]))

    best_name = max(results, key=lambda k: results[k]["roc_auc"])
    print(f"\nBest model by ROC-AUC: {best_name}")

    # Light hyperparameter tuning pass on the winner
    best_pipe = fitted_pipelines[best_name]
    if best_name == "Random Forest":
        param_grid = {
            "model__n_estimators": [200, 300, 400],
            "model__max_depth": [8, 10, 12],
        }
    elif best_name == "XGBoost":
        param_grid = {
            "model__n_estimators": [200, 300],
            "model__max_depth": [3, 4, 5],
            "model__learning_rate": [0.03, 0.05, 0.1],
        }
    elif best_name == "Decision Tree":
        param_grid = {"model__max_depth": [4, 6, 8, 10]}
    else:
        param_grid = {"model__C": [0.1, 1.0, 3.0, 10.0]}

    grid = GridSearchCV(best_pipe, param_grid, scoring="roc_auc", cv=3, n_jobs=-1)
    grid.fit(X_train, y_train)
    tuned_pipe = grid.best_estimator_

    preds = tuned_pipe.predict(X_test)
    proba = tuned_pipe.predict_proba(X_test)[:, 1]
    tuned_metrics = {
        "model_name": best_name,
        "best_params": grid.best_params_,
        "accuracy": accuracy_score(y_test, preds),
        "f1": f1_score(y_test, preds),
        "roc_auc": roc_auc_score(y_test, proba),
        "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
        "comparison": results,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "features": numeric_features + categorical_features,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
    }

    print(f"\n== Tuned {best_name} (final) ==")
    print(f"Accuracy: {tuned_metrics['accuracy']:.4f}")
    print(f"F1: {tuned_metrics['f1']:.4f}")
    print(f"ROC-AUC: {tuned_metrics['roc_auc']:.4f}")
    print("Best params:", grid.best_params_)

    joblib.dump(tuned_pipe, MODEL_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(tuned_metrics, f, indent=2)

    print(f"\nSaved model to {MODEL_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")


if __name__ == "__main__":
    main()
