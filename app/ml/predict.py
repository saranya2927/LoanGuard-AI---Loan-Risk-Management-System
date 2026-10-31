
"""
LoanGuard AI - Applicant-Aware ML Prediction Engine

Supports:
    1. Student
    2. Startup
    3. Investor
    4. Individual

Uses the existing trained pipeline:
    loan_model_v2.pkl

The model feature names and underwriting decision thresholds
are preserved.

Category-specific income mapping:
    Student   -> Actual declared monthly income, if supplied
    Startup   -> Annual business revenue / 12
    Investor  -> Annual investment income / 12
    Individual -> Employment monthly income

Missing income is never fabricated.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# =========================================================
# MODEL CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "loan_model_v2.pkl"

_pipeline = None


def get_pipeline():
    global _pipeline

    if _pipeline is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Loan model not found: {MODEL_PATH}"
            )

        _pipeline = joblib.load(MODEL_PATH)

    return _pipeline


# =========================================================
# SAFE VALUE HELPERS
# =========================================================

def get_number(raw, key, default=0.0):

    value = raw.get(key, default)

    if value is None or value == "":
        return float(default)

    try:
        number = float(value)

        if not np.isfinite(number):
            return float(default)

        return number

    except (TypeError, ValueError):
        return float(default)


def get_text(raw, key, default=""):

    value = raw.get(key, default)

    if value is None:
        return default

    return str(value).strip()


def normalize_applicant_type(raw):

    applicant_type = get_text(
        raw,
        "applicant_type",
        "Individual"
    ).lower()

    allowed_types = {
        "student",
        "startup",
        "investor",
        "individual"
    }

    if applicant_type not in allowed_types:

        raise ValueError(
            f"Unsupported applicant type: {applicant_type}"
        )

    return applicant_type


# =========================================================
# APPLICANT-SPECIFIC FINANCIAL MAPPING
# =========================================================

def get_applicant_financials(raw):
    """
    Converts category-specific financial information into
    the common financial fields used by the trained model.

    Does not invent income or financial information.
    """

    applicant_type = normalize_applicant_type(raw)

    monthly_income = get_number(
        raw,
        "monthly_income"
    )

    other_monthly_income = get_number(
        raw,
        "other_monthly_income"
    )

    employment_years = get_number(
        raw,
        "employment_years"
    )

    employment_type = get_text(
        raw,
        "employment_type"
    )

    # -----------------------------------------------------
    # STUDENT
    # -----------------------------------------------------

    if applicant_type == "student":

        # Only use actual declared income.
        # The current Student form does not collect income.

        employment_type = "Not Applicable"

        employment_years = 0.0

    # -----------------------------------------------------
    # STARTUP
    # -----------------------------------------------------

    elif applicant_type == "startup":

        annual_revenue = get_number(
            raw,
            "startup_annual_revenue"
        )

        # Convert annual business revenue into a monthly
        # revenue proxy for the common model input.
        #
        # This is business revenue, not personal salary.

        if annual_revenue > 0:

            monthly_income = annual_revenue / 12

        employment_type = "Business Owner"

        # Business age is used as a proxy for operating
        # tenure, not as personal employment experience.

        business_age = get_number(
            raw,
            "startup_business_age_years"
        )

        employment_years = business_age

    # -----------------------------------------------------
    # INVESTOR
    # -----------------------------------------------------

    elif applicant_type == "investor":

        annual_investment_income = get_number(
            raw,
            "investor_annual_investment_income"
        )

        # Convert actual annual investment income into
        # monthly investment income.

        if annual_investment_income > 0:

            monthly_income = annual_investment_income / 12

        employment_type = "Not Applicable"

        employment_years = 0.0

    # -----------------------------------------------------
    # INDIVIDUAL
    # -----------------------------------------------------

    elif applicant_type == "individual":

        # Preserve the existing Individual employment data.

        if not employment_type:
            employment_type = "Not Applicable"

    return {
        "applicant_type": applicant_type,
        "employment_type": employment_type,
        "employment_years": employment_years,
        "monthly_income": monthly_income,
        "other_monthly_income": other_monthly_income
    }


# =========================================================
# INTEREST RATE ESTIMATION
# =========================================================

def estimate_interest_rate(credit_score: float) -> float:
    """
    Linear fit against the training data's
    Credit_Score -> Interest_Rate_Percent relationship.
    """

    rate = 17.64 - 0.01406 * credit_score

    return float(
        np.clip(rate, 6.5, 12.5)
    )


# =========================================================
# INCOME STABILITY
# =========================================================

def estimate_income_stability(
    employment_type: str,
    employment_years: float
) -> float:

    type_penalty = {

        "Salaried": 0.0,

        "Contract": 3.0,

        "Business Owner": 4.0,

        "Self-Employed": 5.0,

        "Freelancer": 6.0,

    }.get(employment_type, 5.0)

    years_bonus = min(
        employment_years,
        10.0
    ) * 0.7

    score = 88.0 + years_bonus - type_penalty

    return float(
        np.clip(score, 79.0, 100.0)
    )


# =========================================================
# REPAYMENT CONSISTENCY
# =========================================================

def estimate_repayment_consistency(
    late_payments: float,
    previous_defaults: float,
    credit_history_years: float
) -> float:

    score = (
        100.0
        - late_payments * 4.0
        - previous_defaults * 15.0
    )

    score += min(
        credit_history_years,
        5.0
    ) * 0.5

    return float(
        np.clip(score, 60.0, 100.0)
    )


# =========================================================
# EMI CALCULATION
# =========================================================

def compute_emi(
    principal: float,
    annual_rate_percent: float,
    tenure_months: int
) -> float:

    if tenure_months <= 0:
        return 0.0

    monthly_rate = annual_rate_percent / 12 / 100

    if monthly_rate == 0:
        return principal / tenure_months

    factor = (
        1 + monthly_rate
    ) ** tenure_months

    return (
        principal
        * monthly_rate
        * factor
        / (factor - 1)
    )


# =========================================================
# CREDIT UTILIZATION CATEGORY
# =========================================================

def categorize_utilization(pct: float) -> str:

    if pct <= 30:
        return "Low"

    if pct <= 70:
        return "Medium"

    return "High"


# =========================================================
# BUILD ENGINEERED FEATURES
# =========================================================

def build_features(raw: dict) -> dict:
    """
    Converts applicant-entered data into the full feature
    set expected by loan_model_v2.pkl.
    """

    # -----------------------------------------------------
    # APPLICANT TYPE AND FINANCIAL MAPPING
    # -----------------------------------------------------

    financials = get_applicant_financials(raw)

    applicant_type = financials["applicant_type"]

    employment_type = financials["employment_type"]

    employment_years = financials["employment_years"]

    monthly_income = financials["monthly_income"]

    other_monthly_income = financials["other_monthly_income"]

    # -----------------------------------------------------
    # COMMON INPUT VALUES
    # -----------------------------------------------------

    credit_score = get_number(
        raw,
        "credit_score"
    )

    credit_history_years = get_number(
        raw,
        "credit_history_years"
    )

    credit_utilization = get_number(
        raw,
        "credit_utilization_percent"
    )

    loan_amount = get_number(
        raw,
        "loan_amount"
    )

    loan_tenure_months = int(
        get_number(raw, "loan_tenure_months")
    )

    existing_emi = get_number(
        raw,
        "existing_emi"
    )

    assets = get_number(
        raw,
        "assets"
    )

    liabilities = get_number(
        raw,
        "liabilities"
    )

    bank_balance = get_number(
        raw,
        "bank_balance"
    )

    late_payments = get_number(
        raw,
        "late_payments"
    )

    previous_defaults = get_number(
        raw,
        "previous_defaults"
    )

    # -----------------------------------------------------
    # INTEREST RATE AND EMI
    # -----------------------------------------------------

    interest_rate = estimate_interest_rate(
        credit_score
    )

    new_emi = compute_emi(
        loan_amount,
        interest_rate,
        loan_tenure_months
    )

    total_monthly_obligation = (
        existing_emi + new_emi
    )

    # -----------------------------------------------------
    # INCOME CALCULATIONS
    # -----------------------------------------------------

    total_income = (
        monthly_income + other_monthly_income
    )

    # -----------------------------------------------------
    # ASSET CALCULATIONS
    # -----------------------------------------------------

    net_worth = assets - liabilities

    # -----------------------------------------------------
    # FINANCIAL RATIOS
    # -----------------------------------------------------

    dti_percent = (

        total_monthly_obligation / total_income * 100

        if total_income > 0

        else 0

    )

    emi_to_income_percent = (

        new_emi / total_income * 100

        if total_income > 0

        else 0

    )

    loan_to_income_ratio = (

        loan_amount / (total_income * 12)

        if total_income > 0

        else 0

    )

    networth_to_loan_ratio = (

        net_worth / (loan_amount + 1)

    )

    payment_burden = (

        total_monthly_obligation / (total_income + 1)

    )

    loan_tenure_years = (
        loan_tenure_months / 12
    )

    # -----------------------------------------------------
    # STABILITY AND REPAYMENT SCORES
    # -----------------------------------------------------

    income_stability_score = estimate_income_stability(
        employment_type,
        employment_years
    )

    repayment_consistency_score = estimate_repayment_consistency(
        late_payments,
        previous_defaults,
        credit_history_years
    )

    # -----------------------------------------------------
    # MODEL FEATURES
    #
    # IMPORTANT:
    # Keep these feature names consistent with the
    # original training pipeline.
    # -----------------------------------------------------

    engineered = {

        "Age": get_number(raw, "age"),

        "Gender": get_text(raw, "gender"),

        "Marital_Status": get_text(raw, "marital_status"),

        "Education": get_text(raw, "education"),

        "Employment_Type": employment_type,

        "Employment_Years": employment_years,

        "Monthly_Income": monthly_income,

        "Other_Monthly_Income": other_monthly_income,

        "Credit_Score": credit_score,

        "Credit_History_Years": credit_history_years,

        "Credit_Accounts": get_number(
            raw,
            "credit_accounts"
        ),

        "Credit_Utilization_Percent": credit_utilization,

        "Previous_Loans": get_number(
            raw,
            "previous_loans"
        ),

        "Late_Payments": late_payments,

        "Previous_Defaults": previous_defaults,

        "Loan_Purpose": get_text(
            raw,
            "loan_purpose"
        ),

        "Loan_Amount": loan_amount,

        "Loan_Tenure_Months": loan_tenure_months,

        "Interest_Rate_Percent": interest_rate,

        "Existing_EMI": existing_emi,

        "New_EMI": new_emi,

        "Total_Monthly_Obligation": total_monthly_obligation,

        "DTI_Percent": dti_percent,

        "EMI_to_Income_Percent": emi_to_income_percent,

        "Assets": assets,

        "Liabilities": liabilities,

        "Net_Worth": net_worth,

        "Bank_Balance": bank_balance,

        "Income_Stability_Score": income_stability_score,

        "Repayment_Consistency_Score": repayment_consistency_score,

        "Total_Income": total_income,

        "Loan_to_Income_Ratio": loan_to_income_ratio,

        "NetWorth_to_Loan_Ratio": networth_to_loan_ratio,

        "Credit_Utilization_Category": categorize_utilization(
            credit_utilization
        ),

        "Payment_Burden": payment_burden,

        "Loan_Tenure_Years": loan_tenure_years,

    }

    return engineered


# =========================================================
# UNDERWRITING DECISION
# =========================================================

def decide(
    default_probability_percent: float
) -> tuple[str, str]:
    """
    Existing underwriting policy.

    Below 25%       -> Low / Approve
    25% to below 50% -> Medium / Manual Review
    50% and above   -> High / Reject
    """

    if default_probability_percent < 25:

        return "Low", "Approve"

    if default_probability_percent < 50:

        return "Medium", "Manual Review"

    return "High", "Reject"


# =========================================================
# MAIN PREDICTION FUNCTION
# =========================================================

def predict(raw: dict) -> dict:
    """
    Main LoanGuard prediction function.

    1. Maps applicant-specific financial information.
    2. Builds model features.
    3. Loads the trained pipeline.
    4. Predicts default probability.
    5. Generates risk level and decision.
    """

    # Build engineered features.
    engineered = build_features(raw)

    # Load trained model.
    pipeline = get_pipeline()

    # -----------------------------------------------------
    # VERIFY MODEL FEATURES
    # -----------------------------------------------------

    try:

        feature_order = (
            pipeline
            .named_steps["preprocessor"]
            .feature_names_in_
            .tolist()
        )

    except (AttributeError, KeyError) as error:

        raise RuntimeError(
            "Unable to read the trained model's feature names. "
            "Please verify loan_model_v2.pkl."
        ) from error

    missing_features = [
        feature
        for feature in feature_order
        if feature not in engineered
    ]

    if missing_features:

        raise ValueError(
            "Missing features required by the ML model: "
            + ", ".join(missing_features)
        )

    # -----------------------------------------------------
    # PREPARE INPUT DATAFRAME
    # -----------------------------------------------------

    row = pd.DataFrame(
        [
            {
                key: engineered[key]
                for key in feature_order
            }
        ]
    )

    # -----------------------------------------------------
    # MODEL PREDICTION
    # -----------------------------------------------------

    probability = (
        float(
            pipeline.predict_proba(row)[0, 1]
        ) * 100
    )

    risk_score = round(
        100 - probability,
        1
    )

    risk_level, recommended_decision = decide(
        probability
    )

    # -----------------------------------------------------
    # FINAL RESULT
    # -----------------------------------------------------

    return {

        **engineered,

        "default_probability_percent": round(
            probability,
            2
        ),

        "risk_score": risk_score,

        "risk_level": risk_level,

        "recommended_decision": recommended_decision,

    }
