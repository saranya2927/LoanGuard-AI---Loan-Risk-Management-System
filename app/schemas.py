
import datetime
from typing import Optional, Any

from pydantic import BaseModel, EmailStr, Field


# =========================================================
# AUTHENTICATION SCHEMAS
# =========================================================

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str

    class Config:
        from_attributes = True


# =========================================================
# APPLICATION CREATE SCHEMA
# =========================================================

class ApplicationCreate(BaseModel):

    # Applicant type
    applicant_type: str = "Individual"

    # -----------------------------------------------------
    # PERSONAL INFORMATION
    # -----------------------------------------------------

    full_name: str
    age: int = Field(ge=18, le=100)
    gender: str
    marital_status: str
    education: str

    # -----------------------------------------------------
    # STUDENT ACADEMIC DETAILS
    # -----------------------------------------------------

    student_institution_name: Optional[str] = None
    student_course: Optional[str] = None

    student_year_of_study: Optional[int] = Field(
        default=None,
        ge=0
    )

    student_expected_graduation: Optional[int] = None
    student_education_loan_requirement: Optional[str] = None

    # -----------------------------------------------------
    # STUDENT FINANCIAL SUPPORT DETAILS
    # -----------------------------------------------------

    student_support_source: Optional[str] = None
    student_guardian_relationship: Optional[str] = None
    student_guardian_occupation: Optional[str] = None

    student_guardian_monthly_income: Optional[float] = Field(
        default=None,
        ge=0
    )

    student_scholarship_amount: Optional[float] = Field(
        default=None,
        ge=0
    )

    student_co_applicant_available: Optional[bool] = None
    student_co_applicant_relationship: Optional[str] = None

    # -----------------------------------------------------
    # STARTUP DETAILS
    # -----------------------------------------------------

    startup_name: Optional[str] = None
    startup_business_stage: Optional[str] = None

    startup_business_age_years: Optional[float] = Field(
        default=None,
        ge=0
    )

    startup_annual_revenue: Optional[float] = Field(
        default=None,
        ge=0
    )

    startup_funding_required: Optional[float] = Field(
        default=None,
        ge=0
    )

    startup_existing_funding: Optional[float] = Field(
        default=None,
        ge=0
    )

    # -----------------------------------------------------
    # INVESTOR DETAILS
    # -----------------------------------------------------

    investor_investment_experience: Optional[str] = None

    investor_annual_investment_income: Optional[float] = Field(
        default=None,
        ge=0
    )

    investor_investment_portfolio_value: Optional[float] = Field(
        default=None,
        ge=0
    )

    investor_investment_purpose: Optional[str] = None

    # -----------------------------------------------------
    # INDIVIDUAL DETAILS
    # -----------------------------------------------------

    occupation: Optional[str] = None
    residential_status: Optional[str] = None

    # -----------------------------------------------------
    # EMPLOYMENT AND INCOME
    # -----------------------------------------------------

    employment_type: str = "Not Applicable"

    employment_years: float = Field(
        default=0,
        ge=0
    )

    monthly_income: float = Field(
        default=0,
        ge=0
    )

    other_monthly_income: float = Field(
        default=0,
        ge=0
    )

    # -----------------------------------------------------
    # CREDIT PROFILE
    # -----------------------------------------------------

    credit_score: int = Field(
        ge=300,
        le=900
    )

    credit_history_years: float = Field(
        ge=0
    )

    credit_accounts: int = Field(
        default=0,
        ge=0
    )

    credit_utilization_percent: float = Field(
        default=0,
        ge=0
    )

    previous_loans: int = Field(
        default=0,
        ge=0
    )

    late_payments: int = Field(
        default=0,
        ge=0
    )

    previous_defaults: int = Field(
        default=0,
        ge=0
    )

    # -----------------------------------------------------
    # LOAN DETAILS
    # -----------------------------------------------------

    loan_purpose: str
    loan_amount: float = Field(gt=0)
    loan_tenure_months: int = Field(gt=0)

    existing_emi: float = Field(
        default=0,
        ge=0
    )

    # -----------------------------------------------------
    # ASSETS AND LIABILITIES
    # -----------------------------------------------------

    assets: float = Field(
        default=0,
        ge=0
    )

    liabilities: float = Field(
        default=0,
        ge=0
    )

    bank_balance: float = Field(
        default=0,
        ge=0
    )


# =========================================================
# APPLICATION OUTPUT SCHEMA
# =========================================================

class ApplicationOut(BaseModel):

    id: int
    applicant_type: str

    # -----------------------------------------------------
    # PERSONAL INFORMATION
    # -----------------------------------------------------

    full_name: str
    age: int
    gender: str
    marital_status: str
    education: str

    # -----------------------------------------------------
    # STUDENT ACADEMIC DETAILS
    # -----------------------------------------------------

    student_institution_name: Optional[str] = None
    student_course: Optional[str] = None
    student_year_of_study: Optional[int] = None
    student_expected_graduation: Optional[int] = None
    student_education_loan_requirement: Optional[str] = None

    # -----------------------------------------------------
    # STUDENT FINANCIAL SUPPORT DETAILS
    # -----------------------------------------------------

    student_support_source: Optional[str] = None
    student_guardian_relationship: Optional[str] = None
    student_guardian_occupation: Optional[str] = None
    student_guardian_monthly_income: Optional[float] = None
    student_scholarship_amount: Optional[float] = None
    student_co_applicant_available: Optional[bool] = None
    student_co_applicant_relationship: Optional[str] = None

    # -----------------------------------------------------
    # STARTUP DETAILS
    # -----------------------------------------------------

    startup_name: Optional[str] = None
    startup_business_stage: Optional[str] = None
    startup_business_age_years: Optional[float] = None
    startup_annual_revenue: Optional[float] = None
    startup_funding_required: Optional[float] = None
    startup_existing_funding: Optional[float] = None

    # -----------------------------------------------------
    # INVESTOR DETAILS
    # -----------------------------------------------------

    investor_investment_experience: Optional[str] = None
    investor_annual_investment_income: Optional[float] = None
    investor_investment_portfolio_value: Optional[float] = None
    investor_investment_purpose: Optional[str] = None

    # -----------------------------------------------------
    # INDIVIDUAL DETAILS
    # -----------------------------------------------------

    occupation: Optional[str] = None
    residential_status: Optional[str] = None

    # -----------------------------------------------------
    # EMPLOYMENT AND INCOME
    # -----------------------------------------------------

    employment_type: str
    employment_years: float
    monthly_income: float
    other_monthly_income: float

    # -----------------------------------------------------
    # CREDIT INFORMATION
    # -----------------------------------------------------

    credit_score: int
    credit_history_years: float
    credit_utilization_percent: float
    credit_accounts: int
    previous_loans: int
    late_payments: int
    previous_defaults: int

    # -----------------------------------------------------
    # LOAN INFORMATION
    # -----------------------------------------------------

    loan_purpose: str
    loan_amount: float
    loan_tenure_months: int
    interest_rate_percent: float
    existing_emi: float

    # -----------------------------------------------------
    # ASSETS AND LIABILITIES
    # -----------------------------------------------------

    assets: float
    liabilities: float
    bank_balance: float

    # -----------------------------------------------------
    # CALCULATED FINANCIAL INFORMATION
    # -----------------------------------------------------

    new_emi: Optional[float] = None
    total_monthly_obligation: Optional[float] = None
    total_income: Optional[float] = None
    dti_percent: Optional[float] = None
    emi_to_income_percent: Optional[float] = None
    net_worth: Optional[float] = None
    loan_to_income_ratio: Optional[float] = None
    networth_to_loan_ratio: Optional[float] = None

    credit_utilization_category: Optional[str] = None
    payment_burden: Optional[float] = None
    loan_tenure_years: Optional[float] = None

    income_stability_score: Optional[float] = None
    repayment_consistency_score: Optional[float] = None

    # -----------------------------------------------------
    # MACHINE LEARNING PREDICTION RESULTS
    # -----------------------------------------------------

    default_probability_percent: float
    risk_score: float
    risk_level: str
    recommended_decision: str

    # -----------------------------------------------------
    # APPLICATION STATUS
    # -----------------------------------------------------

    application_status: str
    created_at: datetime.datetime

    # -----------------------------------------------------
    # RECOMMENDATIONS AND GUIDANCE
    # -----------------------------------------------------

    recommendations: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


# =========================================================
# APPLICATION LIST SCHEMA
# =========================================================

class ApplicationListItem(BaseModel):

    id: int
    full_name: str
    loan_amount: float
    loan_purpose: str
    risk_level: str
    recommended_decision: str
    application_status: str
    default_probability_percent: float
    created_at: datetime.datetime

    class Config:
        from_attributes = True
