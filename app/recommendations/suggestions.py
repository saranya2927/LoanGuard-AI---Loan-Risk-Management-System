
"""
LoanGuard AI - Personalized Loan Improvement Suggestions

Generates category-aware financial improvement suggestions
and explains important risk factors.

This module does not modify or retrain the ML model.
"""


def get_risk_factors(raw: dict, prediction: dict) -> list[dict]:
    """
    Identify financial risk factors from applicant information
    and engineered ML prediction features.
    """

    factors = []

    applicant_type = str(
        raw.get("applicant_type", "individual")
    ).strip().lower()

    credit_score = raw.get("credit_score", 0) or 0
    utilization = raw.get("credit_utilization_percent", 0) or 0
    defaults = raw.get("previous_defaults", 0) or 0
    late_payments = raw.get("late_payments", 0) or 0

    dti = prediction.get(
        "dti_percent",
        prediction.get("DTI_Percent", 0)
    ) or 0

    loan_income = prediction.get(
        "loan_to_income_ratio",
        prediction.get("Loan_to_Income_Ratio", 0)
    ) or 0

    monthly_income = raw.get("monthly_income", 0) or 0
    other_monthly_income = raw.get(
        "other_monthly_income", 0
    ) or 0

    income = monthly_income + other_monthly_income

    # -------------------------------------------------
    # CREDIT SCORE
    # -------------------------------------------------

    if credit_score < 650:
        factors.append({
            "factor": "Low Credit Score",
            "severity": "High" if credit_score < 550 else "Medium",
            "value": credit_score,
            "explanation": (
                "Your credit score is below the reference "
                "threshold of 650."
            ),
            "action": (
                "Pay existing credit obligations on time and "
                "regularly monitor your credit report."
            )
        })

    # -------------------------------------------------
    # CREDIT UTILIZATION
    # -------------------------------------------------

    if utilization > 70:
        factors.append({
            "factor": "High Credit Utilization",
            "severity": "High",
            "value": utilization,
            "explanation": (
                "A large percentage of your available credit "
                "is currently being used."
            ),
            "action": (
                "Work towards reducing outstanding credit "
                "balances and avoiding unnecessary borrowing."
            )
        })

    elif utilization > 30:
        factors.append({
            "factor": "Moderate Credit Utilization",
            "severity": "Medium",
            "value": utilization,
            "explanation": (
                "Your credit utilization is above the "
                "30% reference level."
            ),
            "action": (
                "Consider reducing your outstanding credit "
                "balances where financially possible."
            )
        })

    # -------------------------------------------------
    # PREVIOUS DEFAULTS
    # -------------------------------------------------

    if defaults > 0:
        factors.append({
            "factor": "Previous Loan Defaults",
            "severity": "High",
            "value": defaults,
            "explanation": (
                "Previous loan defaults are present "
                "in your supplied financial history."
            ),
            "action": (
                "Resolve outstanding default-related obligations "
                "and maintain consistent repayments."
            )
        })

    # -------------------------------------------------
    # LATE PAYMENTS
    # -------------------------------------------------

    if late_payments > 0:
        factors.append({
            "factor": "Late Repayments",
            "severity": "High" if late_payments >= 3 else "Medium",
            "value": late_payments,
            "explanation": (
                "Your supplied credit history contains "
                "late payment records."
            ),
            "action": (
                "Pay upcoming EMIs and credit bills before "
                "their due dates."
            )
        })

    # -------------------------------------------------
    # DEBT-TO-INCOME RATIO
    # -------------------------------------------------

    if dti > 40:
        factors.append({
            "factor": "High Debt-to-Income Ratio",
            "severity": "High",
            "value": round(dti, 2),
            "explanation": (
                "Your monthly debt obligations consume "
                "a relatively large share of your income."
            ),
            "action": (
                "Consider reducing existing monthly obligations "
                "or choosing a loan amount and tenure that "
                "better fit your repayment capacity."
            )
        })

    elif dti > 30:
        factors.append({
            "factor": "Moderate Debt-to-Income Ratio",
            "severity": "Medium",
            "value": round(dti, 2),
            "explanation": (
                "Your monthly debt obligations are taking "
                "a noticeable share of your income."
            ),
            "action": (
                "Review your existing EMIs and monthly expenses "
                "before taking additional debt."
            )
        })

    # -------------------------------------------------
    # LOAN-TO-INCOME RATIO
    # -------------------------------------------------

    if loan_income > 0.8:
        factors.append({
            "factor": "High Loan-to-Income Ratio",
            "severity": "High",
            "value": round(loan_income, 2),
            "explanation": (
                "The requested loan amount is high relative "
                "to your annual income."
            ),
            "action": (
                "Evaluate a lower loan amount or a repayment "
                "period that is more manageable."
            )
        })

    # -------------------------------------------------
    # INCOME VALIDATION
    # -------------------------------------------------

    # Students may not have personal income.
    # Their education loan repayment may depend on a
    # parent, guardian, scholarship or co-applicant.
    # Therefore, zero personal income alone should not
    # automatically be classified as a High Risk factor.

    if income <= 0 and applicant_type != "student":
        factors.append({
            "factor": "Income Information Needs Review",
            "severity": "High",
            "value": income,
            "explanation": (
                "No positive monthly income was available "
                "for the assessment."
            ),
            "action": (
                "Provide accurate and verifiable income "
                "information appropriate to your applicant category."
            )
        })

    return factors


def get_category_suggestions(
    raw: dict,
    applicant_type: str
) -> list[str]:

    suggestions = []

    applicant_type = str(
        applicant_type or "individual"
    ).strip().lower()

    if applicant_type == "student":

        suggestions.extend([
            "Keep your admission letter and education fee structure ready.",
            "Maintain academic records and required education documents.",
            "Check whether a parent, guardian or co-applicant is required.",
            "Prepare available scholarship, stipend or other financial support details.",
            "Keep parent or guardian income proof and bank statements ready when applicable."
        ])

    elif applicant_type == "startup":

        suggestions.extend([
            "Maintain updated business revenue and expenditure statements.",
            "Keep business registration and ownership documents ready.",
            "Prepare a realistic business plan and funding utilization report.",
            "Maintain clear records of existing business liabilities and funding."
        ])

    elif applicant_type == "investor":

        suggestions.extend([
            "Maintain verified investment income and portfolio statements.",
            "Keep bank statements and investment ownership documents ready.",
            "Prepare details of existing financial commitments.",
            "Maintain records supporting your investment-related income."
        ])

    else:

        suggestions.extend([
            "Maintain stable and verifiable income records.",
            "Keep recent bank statements and salary or business income documents ready.",
            "Maintain a manageable level of existing financial obligations.",
            "Review your monthly budget before requesting additional credit."
        ])

    return suggestions


def get_suggestions(
    raw: dict,
    prediction: dict,
    applicant_type: str = "Individual"
) -> list[str]:
    """
    Generate personalized suggestions using detected risk factors
    and applicant category.
    """

    suggestions = []

    factors = get_risk_factors(raw, prediction)

    # Financial improvement actions
    for factor in factors:
        action = factor.get("action")

        if action and action not in suggestions:
            suggestions.append(action)

    # Applicant-category-specific suggestions
    category_suggestions = get_category_suggestions(
        raw,
        applicant_type
    )

    for suggestion in category_suggestions:
        if suggestion not in suggestions:
            suggestions.append(suggestion)

    if not suggestions:
        suggestions.append(
            "Maintain your current financial profile, "
            "continue timely repayments and regularly monitor "
            "your credit information."
        )

    return suggestions


def explain(
    raw: dict,
    prediction: dict
) -> list[str]:
    """
    Generate understandable explanations of identified
    financial risk factors.

    These are rule-based explanations, not direct proof of
    the ML model's internal decision process.
    """

    factors = get_risk_factors(raw, prediction)

    if not factors:
        return [
            "No major rule-based financial risk flags "
            "were identified from the supplied information."
        ]

    return [
        factor["explanation"]
        for factor in factors
    ]
