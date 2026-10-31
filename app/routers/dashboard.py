import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import require_roles
from app.database import get_db
from app.models import Application, Role

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    user=Depends(require_roles(Role.officer, Role.admin)),
):
    total = db.query(func.count(Application.id)).scalar() or 0
    approved = (
        db.query(func.count(Application.id))
        .filter(Application.recommended_decision == "Approve")
        .scalar()
        or 0
    )
    high_risk = (
        db.query(func.count(Application.id)).filter(Application.risk_level == "High").scalar() or 0
    )
    avg_loan = db.query(func.avg(Application.loan_amount)).scalar() or 0

    risk_distribution = dict(
        db.query(Application.risk_level, func.count(Application.id))
        .group_by(Application.risk_level)
        .all()
    )

    decision_breakdown = dict(
        db.query(Application.recommended_decision, func.count(Application.id))
        .group_by(Application.recommended_decision)
        .all()
    )

    # Applications over the last 6 months (by created_at month)
    since = datetime.datetime.utcnow() - datetime.timedelta(days=182)
    monthly_rows = (
        db.query(
            func.strftime("%Y-%m", Application.created_at).label("month"),
            func.count(Application.id),
        )
        .filter(Application.created_at >= since)
        .group_by("month")
        .order_by("month")
        .all()
    )

    recent = (
        db.query(Application)
        .order_by(Application.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_applications": total,
        "approved_count": approved,
        "approval_rate": round((approved / total * 100), 1) if total else 0,
        "high_risk_count": high_risk,
        "average_loan_amount": round(avg_loan, 2),
        "risk_distribution": {
            "Low": risk_distribution.get("Low", 0),
            "Medium": risk_distribution.get("Medium", 0),
            "High": risk_distribution.get("High", 0),
        },
        "decision_breakdown": {
            "Approve": decision_breakdown.get("Approve", 0),
            "Manual Review": decision_breakdown.get("Manual Review", 0),
            "Reject": decision_breakdown.get("Reject", 0),
        },
        "applications_over_time": [{"month": m, "count": c} for m, c in monthly_rows],
        "recent_applications": [
            {
                "id": a.id,
                "full_name": a.full_name,
                "loan_amount": a.loan_amount,
                "risk_level": a.risk_level,
                "recommended_decision": a.recommended_decision,
                "created_at": a.created_at.isoformat(),
            }
            for a in recent
        ],
    }
