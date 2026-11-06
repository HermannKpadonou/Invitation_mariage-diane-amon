"""Invités : RSVP public (réception des confirmations) + gestion admin."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Guest
from app.schemas import GuestCreate, GuestRead, GuestUpdate, RSVPCreate
from app.utils.auth import get_current_admin
from app.utils import whatsapp_service

router = APIRouter(prefix="/api", tags=["Invités"])

VALID_STATUSES = {"present", "absent", "pending"}


# ── RSVP PUBLIC — réception des confirmations depuis l'invitation ──────────
@router.post("/rsvp", response_model=GuestRead, status_code=status.HTTP_201_CREATED,
             summary="Réception d'une confirmation de présence (public, sans auth)")
def receive_rsvp(body: RSVPCreate, db: Session = Depends(get_db)):
    """Endpoint appelé par la page d'invitation.

    - Si le numéro de téléphone correspond à un invité déjà connu : mise à jour
      de sa réponse (idempotent — l'invité peut modifier sa réponse).
    - Sinon : création d'une nouvelle fiche invité.
    """
    if body.status not in VALID_STATUSES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            f"Statut invalide (attendu : {', '.join(VALID_STATUSES)})")
    if body.companions_count < 0 or body.companions_count > 10:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Nombre d'accompagnants invalide (0–10)")

    phone_norm = whatsapp_service.normalize_phone(body.phone)
    guest = None
    if phone_norm:
        guests_with_phone = db.query(Guest).filter(Guest.phone.isnot(None)).all()
        for g in guests_with_phone:
            if whatsapp_service.normalize_phone(g.phone) == phone_norm:
                guest = g
                break

    if guest is None:
        names = body.first_name.strip().split(" ", 1)
        first = names[0]
        last = names[1] if len(names) > 1 else ""
        guest = Guest(first_name=first, last_name=last or "-")
        db.add(guest)

    guest.phone = body.phone
    guest.status = body.status
    guest.companions_count = body.companions_count
    guest.dietary_options = body.dietary_options
    db.commit()
    db.refresh(guest)
    return guest


@router.get("/rsvp/{phone}", response_model=GuestRead | None,
            summary="Retrouver une réponse par téléphone (public)")
def get_rsvp(phone: str, db: Session = Depends(get_db)):
    guests = db.query(Guest).filter(Guest.phone.isnot(None)).all()
    target = whatsapp_service.normalize_phone(phone)
    for g in guests:
        if whatsapp_service.normalize_phone(g.phone) == target:
            return g
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Aucune réponse trouvée pour ce numéro")


# ── GESTION ADMIN ────────────────────────────────────────────────────────────
@router.get("/guests", response_model=list[GuestRead], summary="Liste des invités (admin)")
def list_guests(db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    return db.query(Guest).order_by(Guest.created_at.desc()).all()


@router.post("/guests", response_model=GuestRead, status_code=status.HTTP_201_CREATED,
             summary="Ajouter un invité (admin)")
def create_guest(body: GuestCreate, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    if body.status not in VALID_STATUSES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Statut invalide")
    guest = Guest(**body.model_dump())
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest


@router.patch("/guests/{guest_id}", response_model=GuestRead, summary="Modifier un invité (admin)")
def update_guest(guest_id: int, body: GuestUpdate, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    guest = db.get(Guest, guest_id)
    if guest is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invité introuvable")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(guest, key, value)
    db.commit()
    db.refresh(guest)
    return guest


@router.delete("/guests/{guest_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer un invité (admin)")
def delete_guest(guest_id: int, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    guest = db.get(Guest, guest_id)
    if guest is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Invité introuvable")
    db.delete(guest)
    db.commit()
