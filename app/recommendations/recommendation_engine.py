
"""
LoanGuard AI - Recommendation and Guidance Engine

Connects ML prediction results with explainable risk factors,
personalized improvement suggestions and reapplication guidance.

This module does not modify or retrain the ML model.
"""

from .suggestions import (
    explain,
    get_suggestions,
    get_risk_factors,
    get_category_suggestions,
)


def estimate_reapplication_period(
    raw: dict,
    prediction: dict,
    risk_factors: list
) -> int:
    """
    Estimate an improvement period based on identified financial
    risk factors.

    This is a rule-based estimate, not a guarantee of approval.
    """

    months = 1

    credit_score = raw.get("credit_score", 0)
    utilization = raw.get("credit_utilization_percent", 0)
    defaults = raw.get("previous_defaults", 0)
    late_payments = raw.get("late_payments", 0)

    dti = prediction.get(
        "dti_percent",
        prediction.get("DTI_Percent", 0)
    )

    decision = prediction.get(
        "recommended_decision", "Manual Review"
    )

    # Credit score improvement
    if credit_score < 550:
        months = max(months, 6)
    elif credit_score < 650:
        months = max(months, 4)

    # Credit utilization
    if utilization > 70:
        months = max(months, 3)
    elif utilization > 30:
        months = max(months, 2)

    # Previous defaults
    if defaults > 0:
        months = max(months, 6)

    # Late repayment history
    if late_payments >= 3:
        months = max(months, 4)
    elif late_payments > 0:
        months = max(months, 2)

    # Debt-to-income ratio
    if dti > 50:
        months = max(months, 4)
    elif dti > 40:
        months = max(months, 3)

    # Multiple significant risk factors
    high_risk_count = sum(
        1 for factor in risk_factors
        if factor.get("severity") == "High"
    )

    if high_risk_count >= 3:
        months = max(months, 6)
    elif high_risk_count >= 2:
        months = max(months, 4)

    # Decision-based minimum guidance
    if decision == "Reject":
        months = max(months, 3)

    elif decision == "Manual Review":
        months = max(months, 1)

    return months


def build_improvement_plan(
    risk_factors: list,
    applicant_type: str
) -> list[dict]:
    """
    Create a prioritized improvement plan.
    """

    plan = []

    for factor in risk_factors:
        plan.append({
            "priority": factor.get("severity", "Medium"),
            "area": factor.get("factor", "Financial Profile"),
            "problem": factor.get("explanation", ""),
            "recommended_action": factor.get("action", "")
        })

    applicant_type = applicant_type.strip().lower()

    if applicant_type == "student":
        plan.append({
            "priority": "Medium",
            "area": "Education Documentation",
            "problem": "Education loan supporting documents may be required.",
            "recommended_action": (
                "Prepare admission confirmation, fee structure, "
                "academic records and applicable financial support documents."
            )
        })

    elif applicant_type == "startup":
        plan.append({
            "priority": "Medium",
            "area": "Business Financial Records",
            "problem": "Business financial information needs to be documented.",
            "recommended_action": (
                "Organize revenue statements, business expenses, "
                "registration documents and funding details."
            )
        })

    elif applicant_type == "investor":
        plan.append({
            "priority": "Medium",
            "area": "Investment Documentation",
            "problem": "Investment-related financial records may be required.",
            "recommended_action": (
                "Prepare investment statements, portfolio details, "
                "bank statements and income records."
            )
        })

    else:
        plan.append({
            "priority": "Medium",
            "area": "Income Documentation",
            "problem": "Verifiable income information is important.",
            "recommended_action": (
                "Maintain recent bank statements, salary slips "
                "or other applicable income proof."
            )
        })

    return plan


def get_document_checklist(applicant_type: str) -> list[str]:
    """
    Generate a category-specific document checklist.

    Actual lender requirements may differ.
    """

    documents = [
        "Identity proof",
        "Address proof",
        "Recent bank statements",
        "Credit report, where available",
        "Existing loan and EMI details"
    ]

    applicant_type = applicant_type.strip().lower()

    if applicant_type == "student":
        documents.extend([
            "Admission letter",
            "Institution fee structure",
            "Academic certificates or mark sheets",
            "Scholarship or financial support details, if applicable",
            "Co-applicant income documents, if required"
        ])

    elif applicant_type == "startup":
        documents.extend([
            "Business registration documents",
            "Business plan",
            "Revenue and expenditure statements",
            "Business bank statements",
            "Funding and liability details"
        ])

    elif applicant_type == "investor":
        documents.extend([
            "Investment portfolio statement",
            "Investment income proof",
            "Demat or investment account statement, if applicable",
            "Details of existing financial commitments"
        ])

    else:
        documents.extend([
            "Salary slips or other income proof",
            "Employment proof, if applicable",
            "Existing loan repayment statements"
        ])

    return documents


def build_reapplication_guidance(
    decision: str,
    estimated_months: int,
    risk_factors: list
) -> str:
    """
    Generate understandable reapplication guidance.
    """

    if decision == "Reject":
        return (
            f"Your application received a rejection under the current "
            f"underwriting policy. Work on the identified financial "
            f"risk factors for approximately {estimated_months} months "
            f"before considering another application. Check your "
            f"updated financial position and lender eligibility "
            f"requirements before reapplying."
        )

    elif decision == "Manual Review":
        return (
            "Your application requires additional underwriting review. "
            "Provide any requested documents and clarify the identified "
            "financial concerns. If improvements are needed, consider "
            f"allowing approximately {estimated_months} months to "
            "address them before a new application."
        )

    return (
        "Your application received an approval recommendation under "
        "the current model policy. Review the lender's final terms, "
        "interest rate and repayment obligations before accepting "
        "any loan offer."
    )


def build_recommendations(
    raw: dict,
    prediction: dict,
    applicant_type: str = "Individual"
) -> dict:
    """
    Main function used by LoanGuard AI.

    Combines:
    - Risk explanations
    - Identified risk factors
    - Personalized suggestions
    - Improvement plan
    - Document checklist
    - Reapplication guidance
    """

    applicant_type = (
        applicant_type or "Individual"
    ).strip().title()

    decision = prediction.get(
        "recommended_decision",
        "Manual Review"
    )

    risk_level = prediction.get(
        "risk_level",
        "Unknown"
    )

    risk_factors = get_risk_factors(
        raw,
        prediction
    )

    explanations = explain(
        raw,
        prediction
    )

    suggestions = get_suggestions(
        raw,
        prediction,
        applicant_type
    )

    category_suggestions = get_category_suggestions(
        raw,
        applicant_type
    )

    estimated_months = estimate_reapplication_period(
        raw,
        prediction,
        risk_factors
    )

    improvement_plan = build_improvement_plan(
        risk_factors,
        applicant_type
    )

    documents = get_document_checklist(
        applicant_type
    )

    guidance = build_reapplication_guidance(
        decision,
        estimated_months,
        risk_factors
    )

    return {
        "applicant_type": applicant_type,

        "recommended_decision": decision,

        "risk_level": risk_level,

        "explanations": explanations,

        "risk_factors": risk_factors,

        "suggestions": suggestions,

        "category_suggestions": category_suggestions,

        "estimated_reapplication_months": (
            estimated_months if decision != "Approve" else None
        ),

        "reapplication_guidance": guidance,

        "improvement_plan": improvement_plan,

        "document_checklist": documents,

        "disclaimer": (
            "The recommendations and reapplication period are "
            "rule-based estimates for guidance only. They do not "
            "guarantee loan approval. Final eligibility and document "
            "requirements depend on the lender's underwriting policy."
        )
    }
