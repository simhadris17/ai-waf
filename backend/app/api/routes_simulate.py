from fastapi import APIRouter, Depends

from app.ml.detector import detector
from app.schemas import SimulateIn, SimulateOut
from app.security import get_current_user

router = APIRouter(prefix="/api/simulate", tags=["simulate"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=SimulateOut)
def simulate(payload: SimulateIn):
    label, confidence, attack_type = detector.predict(payload.text)
    return SimulateOut(
        text=payload.text,
        label=label,
        confidence=confidence,
        attack_type=attack_type if label == "ATTACK" else None,
    )
