
import datetime
import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    JSON,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Role(str, enum.Enum):
    applicant = "applicant"
    officer = "officer"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.applicant)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    applications = relationship("Application", back_populates="applicant_user")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    applicant_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # --- Applicant type ---
    applicant_type = Column(String, nullable=False, default="Individual")

    # --- Personal information ---
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    marital_status = Column(String, nullable=False)
    education = Column(String, nullable=False)

    # --- Student details ---
    student_institution_name = Column(String, nullable=True)
    student_course = Column(String, nullable=True)
    student_year_of_study = Column(Integer, nullable=True)
    student_expected_graduation = Column(Integer, nullable=True)
    student_education_loan_requirement = Column(String, nullable=True)

    # --- Student financial support details ---
    student_support_source = Column(String, nullable=True)
    student_guardian_relationship = Column(String, nullable=True)
    student_guardian_occupation = Column(String, nullable=True)
    student_guardian_monthly_income = Column(Float, nullable=True)
    student_scholarship_amount = Column(Float, nullable=True)
    student_co_applicant_available = Column(Boolean, nullable=True)
    student_co_applicant_relationship = Column(String, nullable=True)

    # --- Startup details ---
    startup_name = Column(String, nullable=True)
    startup_business_stage = Column(String, nullable=True)
    startup_business_age_years = Column(Float, nullable=True)
    startup_annual_revenue = Column(Float, nullable=True)
    startup_funding_required = Column(Float, nullable=True)
    startup_existing_funding = Column(Float, nullable=True)

    # --- Investor details ---
    investor_investment_experience = Column(String, nullable=True)
    investor_annual_investment_income = Column(Float, nullable=True)
    investor_investment_portfolio_value = Column(Float, nullable=True)
    investor_investment_purpose = Column(String, nullable=True)

    # --- Individual details ---
    occupation = Column(String, nullable=True)
    residential_status = Column(String, nullable=True)

    # --- Employment & income ---
    employment_type = Column(String, nullable=False)
    employment_years = Column(Float, nullable=False)
    monthly_income = Column(Float, nullable=False)
    other_monthly_income = Column(Float, default=0)

    # --- Credit profile ---
    credit_score = Column(Integer, nullable=False)
    credit_history_years = Column(Float, nullable=False)
    credit_accounts = Column(Integer, default=0)
    credit_utilization_percent = Column(Float, default=0)
    previous_loans = Column(Integer, default=0)
    late_payments = Column(Integer, default=0)
    previous_defaults = Column(Integer, default=0)

    # --- Loan details ---
    loan_purpose = Column(String, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_tenure_months = Column(Integer, nullable=False)
    interest_rate_percent = Column(Float, nullable=False)
    existing_emi = Column(Float, default=0)

    # --- Assets & liabilities ---
    assets = Column(Float, default=0)
    liabilities = Column(Float, default=0)
    bank_balance = Column(Float, default=0)

    # --- Engineered / computed fields ---
    new_emi = Column(Float)
    total_monthly_obligation = Column(Float)
    total_income = Column(Float)
    dti_percent = Column(Float)
    emi_to_income_percent = Column(Float)
    net_worth = Column(Float)
    loan_to_income_ratio = Column(Float)
    networth_to_loan_ratio = Column(Float)
    credit_utilization_category = Column(String)
    payment_burden = Column(Float)
    loan_tenure_years = Column(Float)
    income_stability_score = Column(Float)
    repayment_consistency_score = Column(Float)

    # --- Model output ---
    default_probability_percent = Column(Float)
    risk_score = Column(Float)
    risk_level = Column(String)
    recommended_decision = Column(String)
    application_status = Column(String, default="Submitted")

    # --- Recommendation & guidance output ---
    recommendations = Column(JSON, nullable=True)

    # --- Application metadata ---
    is_historical = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    applicant_user = relationship("User", back_populates="applications")
