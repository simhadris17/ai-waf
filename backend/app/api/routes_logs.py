from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RequestLog
from app.schemas import LogOut, StatsOut
from app.security import get_current_user

router = APIRouter(prefix="/api/logs", tags=["logs"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=list[LogOut])
def list_logs(
    limit: int = Query(50, ge=1, le=500),
    label: str | None = Query(None, description="Filter by SAFE or ATTACK"),
    search: str | None = Query(None, description="Substring search on path"),
    db: Session = Depends(get_db),
):
    query = db.query(RequestLog)
    if label:
        query = query.filter(RequestLog.label == label.upper())
    if search:
        query = query.filter(RequestLog.path.ilike(f"%{search}%"))
    return query.order_by(RequestLog.created_at.desc()).limit(limit).all()


@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(RequestLog.id)).scalar() or 0
    safe = db.query(func.count(RequestLog.id)).filter(RequestLog.label == "SAFE").scalar() or 0
    attack = db.query(func.count(RequestLog.id)).filter(RequestLog.label == "ATTACK").scalar() or 0
    blocked = db.query(func.count(RequestLog.id)).filter(RequestLog.blocked == 1).scalar() or 0
    avg_conf = db.query(func.avg(RequestLog.confidence)).scalar() or 0.0

    return StatsOut(
        total=total,
        safe=safe,
        attack=attack,
        blocked=blocked,
        avg_confidence=round(float(avg_conf), 4),
    )
