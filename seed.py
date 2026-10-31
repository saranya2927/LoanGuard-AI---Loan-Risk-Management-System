"""
Seeds the database with:
  - one Admin, one Loan Officer, and one demo Applicant account
  - ~180 historical applications sampled from your real dataset, so the
    Dashboard and Application History pages aren't empty on first run

Run once, after training the model:
    python3 seed.py
"""
import datetime
import random
from pathlib import Path

import pandas as pd

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.models import Application, Role, User

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "LoanGuard_AI_Final_Preprocessed_Dataset.csv"

random.seed(7)

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def seed_users():
    demo_users = [
        ("LoanGuard Admin", "admin@loanguard.ai", "Admin@123", Role.admin),
        ("Priya Krishnan", "officer@loanguard.ai", "Officer@123", Role.officer),
        ("Demo Applicant", "applicant@loanguard.ai", "Applicant@123", Role.applicant),
    ]
    created = []
    for full_name, email, password, role in demo_users:
        if db.query(User).filter(User.email == email).first():
            continue
        password_hash, salt = hash_password(password)
        user = User(full_name=full_name, email=email, password_hash=password_hash, salt=salt, role=role)
        db.add(user)
        created.append(email)
    db.commit()
    if created:
        print("Created demo accounts:", ", ".join(created))
    else:
        print("Demo accounts already exist, skipping.")


def seed_applications(n=180):
    if db.query(Application).filter(Application.is_historical == True).count() > 0:  # noqa: E712
        print("Historical applications already seeded, skipping.")
        return

    df = pd.read_csv(DATA_PATH).sample(n=n, random_state=7).reset_index(drop=True)
    now = datetime.datetime.utcnow()

    for _, row in df.iterrows():
        days_ago = random.randint(0, 180)
        created_at = now - datetime.timedelta(days=days_ago, hours=random.randint(0, 23))

        application = Application(
            applicant_user_id=None,
            full_name=row["Name"],
            age=int(row["Age"]),
            gender=row["Gender"],
            marital_status=row["Marital_Status"],
            education=row["Education"],
            employment_type=row["Employment_Type"],
            employment_years=row["Employment_Years"],
            monthly_income=row["Monthly_Income"],
            other_monthly_income=row["Other_Monthly_Income"],
            credit_score=int(row["Credit_Score"]),
            credit_history_years=row["Credit_History_Years"],
            credit_accounts=int(row["Credit_Accounts"]),
            credit_utilization_percent=row["Credit_Utilization_Percent"],
            previous_loans=int(row["Previous_Loans"]),
            late_payments=int(row["Late_Payments"]),
            previous_defaults=int(row["Previous_Defaults"]),
            loan_purpose=row["Loan_Purpose"],
            loan_amount=row["Loan_Amount"],
            loan_tenure_months=int(row["Loan_Tenure_Months"]),
            interest_rate_percent=row["Interest_Rate_Percent"],
            existing_emi=row["Existing_EMI"],
            assets=row["Assets"],
            liabilities=row["Liabilities"],
            bank_balance=row["Bank_Balance"],
            new_emi=row["New_EMI"],
            total_monthly_obligation=row["Total_Monthly_Obligation"],
            total_income=row["Total_Income"],
            dti_percent=row["DTI_Percent"],
            emi_to_income_percent=row["EMI_to_Income_Percent"],
            net_worth=row["Net_Worth"],
            loan_to_income_ratio=row["Loan_to_Income_Ratio"],
            networth_to_loan_ratio=row["NetWorth_to_Loan_Ratio"],
            credit_utilization_category=row["Credit_Utilization_Category"],
            payment_burden=row["Payment_Burden"],
            loan_tenure_years=row["Loan_Tenure_Years"],
            income_stability_score=row["Income_Stability_Score"],
            repayment_consistency_score=row["Repayment_Consistency_Score"],
            default_probability_percent=row["Default_Probability_Percent"],
            risk_score=row["Risk_Score"],
            risk_level=row["Risk_Level"],
            recommended_decision=row["Recommended_Decision"],
            application_status=row["Application_Status"],
            is_historical=True,
            created_at=created_at,
        )
        db.add(application)

    db.commit()
    print(f"Seeded {n} historical applications.")


if __name__ == "__main__":
    seed_users()
    seed_applications()
    db.close()
    print("Done.")
