"""Statistiques du mariage (admin) + ping de visite (public)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Guest
from app.schemas import StatsResponse
from app.utils.auth import get_current_admin
from app.utils import notify

router = APIRouter(prefix="/api/stats", tags=["Statistiques"])


@router.get("", response_model=StatsResponse, summary="Tableau de bord (admin)")
def get_stats(db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    guests = db.query(Guest).all()
    return StatsResponse(
        total_guests=len(guests),
        total_present=sum(1 for g in guests if g.status == "present"),
        total_absent=sum(1 for g in guests if g.status == "absent"),
        total_pending=sum(1 for g in guests if g.status == "pending"),
        total_companions=sum(g.companions_count or 0 for g in guests if g.status == "present"),
    )


# ── Ping de visite (public) — appelé par index.html à chaque session ────────
@router.post("/visit", status_code=204, summary="Ping de visite (public, sans auth)")
async def ping_visit():
    """Comptabilise une visite de l'invitation.

    Les visites sont agrégées : au plus une notification aux mariés toutes
    les VISIT_NOTIFY_MINUTES minutes (sinon chaque rafraîchissement de page
    générerait un message).
    """
    await notify.notify_visit()
