
import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_roles
from app.database import get_db
from app.ml.predict import predict
from app.models import Application, Role, User
from app.schemas import ApplicationCreate, ApplicationListItem, ApplicationOut
from app.recommendations.recommendation_engine import build_recommendations


router = APIRouter(prefix="/api/applications", tags=["applications"])


# =========================================================
# CONVERT APPLICATION PAYLOAD INTO DATABASE RECORD
# =========================================================

def _to_application_row(
    payload: ApplicationCreate,
    result: dict,
    recommendations: dict,
    user: Optional[User]
) -> Application:

    return Application(

        # -------------------------------------------------
        # USER INFORMATION
        # -------------------------------------------------

        applicant_user_id=(
            user.id if user and user.role == Role.applicant else None
        ),

        applicant_type=payload.applicant_type,

        # -------------------------------------------------
        # PERSONAL INFORMATION
        # -------------------------------------------------

        full_name=payload.full_name,
        age=payload.age,
        gender=payload.gender,
        marital_status=payload.marital_status,
        education=payload.education,

        # -------------------------------------------------
        # STUDENT ACADEMIC DETAILS
        # -------------------------------------------------

        student_institution_name=payload.student_institution_name,
        student_course=payload.student_course,
        student_year_of_study=payload.student_year_of_study,
        student_expected_graduation=payload.student_expected_graduation,
        student_education_loan_requirement=(
            payload.student_education_loan_requirement
        ),

        # -------------------------------------------------
        # STUDENT FINANCIAL SUPPORT DETAILS
        # -------------------------------------------------

        student_support_source=payload.student_support_source,
        student_guardian_relationship=(
            payload.student_guardian_relationship
        ),
        student_guardian_occupation=payload.student_guardian_occupation,
        student_guardian_monthly_income=(
            payload.student_guardian_monthly_income
        ),
        student_scholarship_amount=payload.student_scholarship_amount,
        student_co_applicant_available=(
            payload.student_co_applicant_available
        ),
        student_co_applicant_relationship=(
            payload.student_co_applicant_relationship
        ),

        # -------------------------------------------------
        # STARTUP DETAILS
        # -------------------------------------------------

        startup_name=payload.startup_name,
        startup_business_stage=payload.startup_business_stage,
        startup_business_age_years=payload.startup_business_age_years,
        startup_annual_revenue=payload.startup_annual_revenue,
        startup_funding_required=payload.startup_funding_required,
        startup_existing_funding=payload.startup_existing_funding,

        # -------------------------------------------------
        # INVESTOR DETAILS
        # -------------------------------------------------

        investor_investment_experience=(
            payload.investor_investment_experience
        ),
        investor_annual_investment_income=(
            payload.investor_annual_investment_income
        ),
        investor_investment_portfolio_value=(
            payload.investor_investment_portfolio_value
        ),
        investor_investment_purpose=(
            payload.investor_investment_purpose
        ),

        # -------------------------------------------------
        # INDIVIDUAL DETAILS
        # -------------------------------------------------

        occupation=payload.occupation,
        residential_status=payload.residential_status,

        # -------------------------------------------------
        # EMPLOYMENT AND INCOME
        # -------------------------------------------------

        employment_type=payload.employment_type,
        employment_years=payload.employment_years,
        monthly_income=payload.monthly_income,
        other_monthly_income=payload.other_monthly_income,

        # -------------------------------------------------
        # CREDIT PROFILE
        # -------------------------------------------------

        credit_score=payload.credit_score,
        credit_history_years=payload.credit_history_years,
        credit_accounts=payload.credit_accounts,
        credit_utilization_percent=payload.credit_utilization_percent,
        previous_loans=payload.previous_loans,
        late_payments=payload.late_payments,
        previous_defaults=payload.previous_defaults,

        # -------------------------------------------------
        # LOAN DETAILS
        # -------------------------------------------------

        loan_purpose=payload.loan_purpose,
        loan_amount=payload.loan_amount,
        loan_tenure_months=payload.loan_tenure_months,

        interest_rate_percent=result["Interest_Rate_Percent"],

        existing_emi=payload.existing_emi,

        # -------------------------------------------------
        # ASSETS AND LIABILITIES
        # -------------------------------------------------

        assets=payload.assets,
        liabilities=payload.liabilities,
        bank_balance=payload.bank_balance,

        # -------------------------------------------------
        # ENGINEERED FEATURES
        # -------------------------------------------------

        new_emi=result["New_EMI"],
        total_monthly_obligation=result["Total_Monthly_Obligation"],
        total_income=result["Total_Income"],
        dti_percent=result["DTI_Percent"],
        emi_to_income_percent=result["EMI_to_Income_Percent"],
        net_worth=result["Net_Worth"],
        loan_to_income_ratio=result["Loan_to_Income_Ratio"],
        networth_to_loan_ratio=result["NetWorth_to_Loan_Ratio"],
        credit_utilization_category=result["Credit_Utilization_Category"],
        payment_burden=result["Payment_Burden"],
        loan_tenure_years=result["Loan_Tenure_Years"],
        income_stability_score=result["Income_Stability_Score"],
        repayment_consistency_score=result["Repayment_Consistency_Score"],

        # -------------------------------------------------
        # ML PREDICTION RESULTS
        # -------------------------------------------------

        default_probability_percent=result["default_probability_percent"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        recommended_decision=result["recommended_decision"],

        # -------------------------------------------------
        # RECOMMENDATIONS AND GUIDANCE
        # -------------------------------------------------

        recommendations=recommendations,

        application_status="Decisioned",
    )


# =========================================================
# SUBMIT LOAN APPLICATION
# =========================================================

@router.post("", response_model=ApplicationOut)
def submit_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    try:
        # Convert application details into dictionary
        raw_data = payload.model_dump()

        # Step 1: Generate ML prediction
        result = predict(raw_data)

        # Step 2: Generate recommendations
        recommendations = build_recommendations(
            raw=raw_data,
            prediction=result,
            applicant_type=payload.applicant_type
        )

        # Step 3: Create database application record
        application = _to_application_row(
            payload=payload,
            result=result,
            recommendations=recommendations,
            user=user
        )

        # Step 4: Save application and recommendations
        db.add(application)
        db.commit()
        db.refresh(application)

        return application

    except Exception:
        db.rollback()
        raise


# =========================================================
# GET LOGGED-IN APPLICANT APPLICATIONS
# =========================================================

@router.get("/mine", response_model=list[ApplicationListItem])
def my_applications(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    return (
        db.query(Application)
        .filter(Application.applicant_user_id == user.id)
        .order_by(Application.created_at.desc())
        .all()
    )


# =========================================================
# GET ALL APPLICATIONS - OFFICER / ADMIN
# =========================================================

@router.get("", response_model=list[ApplicationListItem])
def list_applications(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.officer, Role.admin)),
    search: Optional[str] = None,
    risk_level: Optional[str] = None,
    decision: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):

    q = db.query(Application)

    if search:
        like = f"%{search}%"

        q = q.filter(
            or_(
                Application.full_name.ilike(like),
                Application.loan_purpose.ilike(like)
            )
        )

    if risk_level:
        q = q.filter(Application.risk_level == risk_level)

    if decision:
        q = q.filter(
            Application.recommended_decision == decision
        )

    q = q.order_by(Application.created_at.desc())

    return q.offset(
        (page - 1) * page_size
    ).limit(page_size).all()


# =========================================================
# GET SINGLE APPLICATION WITH RECOMMENDATIONS
# =========================================================

@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    application = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    if (
        user.role == Role.applicant
        and application.applicant_user_id != user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    return application


# =========================================================
# EXPORT APPLICATION AS CSV
# =========================================================

@router.get("/{application_id}/export.csv")
def export_application_csv(
    application_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    application = (
        db.query(Application)
        .filter(Application.id == application_id)
        .first()
    )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    if (
        user.role == Role.applicant
        and application.applicant_user_id != user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["Field", "Value"])

    for column in Application.__table__.columns:

        value = getattr(application, column.name)

        if isinstance(value, (dict, list)):
            value = str(value)

        writer.writerow([column.name, value])

    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename=loanguard_report_{application_id}.csv"
        },
    )
