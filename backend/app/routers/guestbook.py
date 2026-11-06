"""Livre d'or public : les mots doux laissés par les invités.

- GET  /api/guestbook : les derniers messages (lus par l'invitation).
- POST /api/guestbook : publier un message (public, sans auth).
Les messages sont stockés en base → ils restent visibles pour tout
le monde, sur tous les appareils, même après un redéploiement
(lorsqu'une base permanente est branchée via DATABASE_URL).
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GuestbookEntry
from app.schemas import GuestbookCreate, GuestbookRead
from app.utils.auth import get_current_admin
from app.utils import notify

router = APIRouter(prefix="/api/guestbook", tags=["Livre d'or"])

MAX_MESSAGES = 500  # garde-fou anti-spam : les plus anciens sont retirés


@router.get("", response_model=list[GuestbookRead],
            summary="Lister les messages du livre d'or (public)")
def list_messages(limit: int = Query(default=100, le=200), db: Session = Depends(get_db)):
    return (
        db.query(GuestbookEntry)
        .order_by(GuestbookEntry.created_at.desc(), GuestbookEntry.id.desc())
        .limit(limit)
        .all()
    )


@router.post("", response_model=GuestbookRead, status_code=status.HTTP_201_CREATED,
             summary="Publier un message dans le livre d'or (public, sans auth)")
def create_message(body: GuestbookCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    name = body.name.strip()
    message = body.message.strip()
    if len(name) < 2 or len(message) < 2:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Indiquez au moins votre petit nom et quelques mots doux.")
    entry = GuestbookEntry(name=name, message=message)
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Notification des mariés (email + WhatsApp) — en arrière-plan.
    background_tasks.add_task(notify.notify_guestbook, name=entry.name, message=entry.message)

    # Garde-fou : on ne conserve que les MAX_MESSAGES derniers messages
    total = db.query(GuestbookEntry).count()
    if total > MAX_MESSAGES:
        ids_a_garder = [
            row.id for row in db.query(GuestbookEntry.id)
            .order_by(GuestbookEntry.created_at.desc(), GuestbookEntry.id.desc())
            .limit(MAX_MESSAGES).all()
        ]
        db.query(GuestbookEntry).filter(~GuestbookEntry.id.in_(ids_a_garder)).delete(synchronize_session=False)
        db.commit()

    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Supprimer un message (admin)")
def delete_message(entry_id: int, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    entry = db.get(GuestbookEntry, entry_id)
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Message introuvable")
    db.delete(entry)
    db.commit()
