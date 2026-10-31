from fastapi import APIRouter

from app.ml.predict import predict
from app.schemas import ApplicationCreate

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.post("/predict")
def demo_predict(payload: ApplicationCreate):
    """Same trained model as the real application flow, but stateless and
    open to the public - powers the interactive gauge on the landing page."""
    result = predict(payload.model_dump())
    return {
        "default_probability_percent": result["default_probability_percent"],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "recommended_decision": result["recommended_decision"],
    }
