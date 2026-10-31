
"""
LoanGuard AI - Model Training Script (V2)
------------------------------------------

Dataset:
    loanguard/data/LoanGuard_AI_Final_Preprocessed_Dataset_v2.csv

Model:
    loanguard/app/ml/loan_model_v2.pkl

Metrics:
    loanguard/app/ml/model_metrics_v2.json

Workflow:
    1. Load the preprocessed dataset.
    2. Remove leakage and redundant columns.
    3. Split data into training and testing sets.
    4. Train a Gradient Boosting Classifier.
    5. Tune hyperparameters using GridSearchCV.
    6. Evaluate training and testing performance.
    7. Perform 5-fold cross-validation.
    8. Save the trained model and evaluation metrics.

Run from the inner project root:
    python ml_v2_training/train_model_v2.py
"""

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from sklearn.model_selection import (
    GridSearchCV,
    StratifiedKFold,
    cross_validate,
    train_test_split,
)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


warnings.filterwarnings("ignore")


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

# Actual project root: loanguard/
PROJECT_ROOT = BASE_DIR.parent

# Dataset location
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "LoanGuard_AI_Final_Preprocessed_Dataset_v2.csv"
)

# Save model where predict.py expects it
MODEL_PATH = (
    PROJECT_ROOT
    / "app"
    / "ml"
    / "loan_model_v2.pkl"
)

# Save evaluation metrics
METRICS_PATH = (
    PROJECT_ROOT
    / "app"
    / "ml"
    / "model_metrics_v2.json"
)


# --------------------------------------------------
# 2. CONFIGURATION
# --------------------------------------------------

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

REDUNDANT_COLUMNS = [
    "Loan_Tenure_Years",
    "Assets",
    "Total_Income",
    "Total_Monthly_Obligation",
    "EMI_to_Income_Percent",
    "Payment_Burden",
    "Liabilities",
]

TARGET = "Default_Flag"

CV = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)


# --------------------------------------------------
# 3. MODEL EVALUATION FUNCTION
# --------------------------------------------------

def evaluate(pipe, X_train, y_train, X_test, y_test):

    train_predictions = pipe.predict(X_train)

    test_predictions = pipe.predict(X_test)

    test_probabilities = pipe.predict_proba(X_test)[:, 1]

    return {
        "train_accuracy": accuracy_score(
            y_train,
            train_predictions
        ),

        "accuracy": accuracy_score(
            y_test,
            test_predictions
        ),

        "precision_default": precision_score(
            y_test,
            test_predictions,
            zero_division=0
        ),

        "recall_default": recall_score(
            y_test,
            test_predictions,
            zero_division=0
        ),

        "f1": f1_score(
            y_test,
            test_predictions,
            zero_division=0
        ),

        "roc_auc": roc_auc_score(
            y_test,
            test_probabilities
        ),
    }


# --------------------------------------------------
# 4. MAIN TRAINING FUNCTION
# --------------------------------------------------

def main():

    print("\n========================================")
    print("       LOANGUARD AI MODEL TRAINING")
    print("========================================")

    # Check dataset availability

    if not DATA_PATH.exists():

        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    print("\nLoading dataset...")

    df = pd.read_csv(DATA_PATH)

    print("Dataset shape:", df.shape)

    # Check target column

    if TARGET not in df.columns:

        raise ValueError(
            f"Target column '{TARGET}' not found."
        )

    # Check required columns

    required_columns = (
        LEAK_COLUMNS + REDUNDANT_COLUMNS
    )

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Required dataset columns are missing: {missing_columns}"
        )

    # Check target values

    if df[TARGET].isnull().any():

        raise ValueError(
            "Target column contains missing values."
        )

    if set(df[TARGET].unique()) != {0, 1}:

        raise ValueError(
            "Default_Flag must contain exactly classes 0 and 1."
        )

    # --------------------------------------------------
    # 5. REMOVE LEAKAGE AND REDUNDANT COLUMNS
    # --------------------------------------------------

    print("\nRemoving leakage columns...")

    X = df.drop(
        columns=LEAK_COLUMNS + REDUNDANT_COLUMNS + [TARGET]
    )

    y = df[TARGET]

    print("Remaining features:", X.shape[1])

    # Identify numeric and categorical features

    numeric_features = X.select_dtypes(
        include=[np.number]
    ).columns.tolist()

    categorical_features = X.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    print(
        "Numeric features:",
        len(numeric_features)
    )

    print(
        "Categorical features:",
        len(categorical_features)
    )

    # --------------------------------------------------
    # 6. TRAIN-TEST SPLIT
    # --------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print("\nTraining samples:", len(X_train))

    print("Testing samples:", len(X_test))

    # --------------------------------------------------
    # 7. DATA PREPROCESSING
    # --------------------------------------------------

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                StandardScaler(),
                numeric_features,
            ),

            (
                "cat",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features,
            ),
        ]
    )

    # --------------------------------------------------
    # 8. GRADIENT BOOSTING MODEL
    # --------------------------------------------------

    base_pipe = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),

            (
                "model",
                GradientBoostingClassifier(
                    random_state=42
                ),
            ),
        ]
    )

    # --------------------------------------------------
    # 9. HYPERPARAMETER TUNING
    # --------------------------------------------------

    print("\nStarting hyperparameter tuning...")

    param_grid = {
        "model__n_estimators": [150, 200],

        "model__max_depth": [2, 3],

        "model__learning_rate": [0.05, 0.08],

        "model__subsample": [0.85, 1.0],

        "model__min_samples_leaf": [15, 25],
    }

    search = GridSearchCV(
        estimator=base_pipe,
        param_grid=param_grid,
        scoring="f1",
        cv=3,
        n_jobs=-1,
        verbose=1,
    )

    search.fit(
        X_train,
        y_train
    )

    tuned_pipe = search.best_estimator_

    print("\nBest parameters:")

    print(search.best_params_)

    # --------------------------------------------------
    # 10. TRAINING AND TESTING EVALUATION
    # --------------------------------------------------

    print("\nEvaluating trained model...")

    tuned_eval = evaluate(
        tuned_pipe,
        X_train,
        y_train,
        X_test,
        y_test,
    )

    predictions = tuned_pipe.predict(X_test)

    # --------------------------------------------------
    # 11. FIVE-FOLD CROSS VALIDATION
    # --------------------------------------------------

    print("\nRunning 5-fold cross-validation...")

    final_pipeline_for_cv = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor,
            ),

            (
                "model",
                tuned_pipe.named_steps["model"],
            ),
        ]
    )

    cv_results = cross_validate(
        final_pipeline_for_cv,
        X,
        y,
        cv=CV,
        n_jobs=2,

        scoring={
            "accuracy": "accuracy",
            "precision": "precision",
            "recall": "recall",
            "f1": "f1",
            "roc_auc": "roc_auc",
        },
    )

    # --------------------------------------------------
    # 12. FINAL METRICS
    # --------------------------------------------------

    metrics = {

        "model_name": "GradientBoosting (tuned)",

        "best_params": search.best_params_,

        "train_accuracy": tuned_eval["train_accuracy"],

        "accuracy": tuned_eval["accuracy"],

        "precision_default": tuned_eval["precision_default"],

        "recall_default": tuned_eval["recall_default"],

        "f1": tuned_eval["f1"],

        "roc_auc": tuned_eval["roc_auc"],

        "overfit_gap": (
            tuned_eval["train_accuracy"]
            - tuned_eval["accuracy"]
        ),

        "cv_accuracy_mean": float(
            cv_results["test_accuracy"].mean()
        ),

        "cv_accuracy_std": float(
            cv_results["test_accuracy"].std()
        ),

        "cv_precision_default_mean": float(
            cv_results["test_precision"].mean()
        ),

        "cv_recall_default_mean": float(
            cv_results["test_recall"].mean()
        ),

        "cv_f1_default_mean": float(
            cv_results["test_f1"].mean()
        ),

        "cv_roc_auc_mean": float(
            cv_results["test_roc_auc"].mean()
        ),

        "confusion_matrix": confusion_matrix(
            y_test,
            predictions,
        ).tolist(),

        "classification_report": classification_report(
            y_test,
            predictions,
            target_names=[
                "No Default",
                "Default",
            ],
            output_dict=True,
            zero_division=0,
        ),

        "n_train": len(X_train),

        "n_test": len(X_test),

        "n_total": len(df),

        "dropped_redundant_columns": REDUNDANT_COLUMNS,

        "features": (
            numeric_features + categorical_features
        ),

        "numeric_features": numeric_features,

        "categorical_features": categorical_features,

        "class_balance": {
            "no_default": int((y == 0).sum()),

            "default": int((y == 1).sum()),
        },

        "dataset_version": (
            "v2 (regenerated, 6000 rows, "
            "Previous_Defaults carries real signal)"
        ),
    }

    # --------------------------------------------------
    # 13. DISPLAY MODEL PERFORMANCE
    # --------------------------------------------------

    print("\n========================================")

    print("           MODEL PERFORMANCE")

    print("========================================")

    print(
        f"Train Accuracy: "
        f"{metrics['train_accuracy']:.4f}"
    )

    print(
        f"Test Accuracy:  "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        f"Overfit Gap:    "
        f"{metrics['overfit_gap']:+.4f}"
    )

    print(
        f"Precision:      "
        f"{metrics['precision_default']:.4f}"
    )

    print(
        f"Recall:         "
        f"{metrics['recall_default']:.4f}"
    )

    print(
        f"F1 Score:       "
        f"{metrics['f1']:.4f}"
    )

    print(
        f"ROC-AUC:        "
        f"{metrics['roc_auc']:.4f}"
    )

    print(
        f"5-fold CV Accuracy: "
        f"{metrics['cv_accuracy_mean']:.4f} "
        f"+/- {metrics['cv_accuracy_std']:.4f}"
    )

    print(
        "\nConfusion Matrix [[TN, FP], [FN, TP]]:"
    )

    print(metrics["confusion_matrix"])

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            target_names=[
                "No Default",
                "Default",
            ],
            zero_division=0,
        )
    )

    # --------------------------------------------------
    # 14. SAVE MODEL AND METRICS
    # --------------------------------------------------

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("\nSaving trained model...")

    joblib.dump(
        tuned_pipe,
        MODEL_PATH,
    )

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics,
            file,
            indent=4,
        )

    print("\n========================================")

    print("          TRAINING COMPLETED")

    print("========================================")

    print("\nSaved model:")

    print(MODEL_PATH)

    print("\nSaved metrics:")

    print(METRICS_PATH)


# --------------------------------------------------
# 15. EXECUTION
# --------------------------------------------------

if __name__ == "__main__":
    main()
