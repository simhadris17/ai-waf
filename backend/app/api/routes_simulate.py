from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.detector import detector
from app.models import RequestLog
from app.schemas import SimulateIn, SimulateOut
from app.security import get_current_user

router = APIRouter(prefix="/api/simulate", tags=["simulate"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=SimulateOut)
def simulate(
    payload: SimulateIn,
    request: Request,
    db: Session = Depends(get_db),
):
    label, confidence, attack_type = detector.predict(payload.text)
    db.add(RequestLog(
        client_ip=request.client.host if request.client else None,
        method="SCAN",
        path=payload.text,
        label=label,
        confidence=confidence,
        blocked=int(label == "ATTACK"),
    ))
    db.commit()
    return SimulateOut(
        text=payload.text,
        label=label,
        confidence=confidence,
        attack_type=attack_type if label == "ATTACK" else None,
    )
