"""Envoi de messages WhatsApp : invitation, rappels, remerciements.

Deux modes selon la configuration (voir app/utils/whatsapp_service.py) :
- **api**  : WhatsApp Cloud API de Meta (réel, nécessite .env)
- **link** : liens wa.me clic-à-envoyer (gratuit, fonctionne sans clé)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Guest
from app.utils.auth import get_current_admin
from app.utils import whatsapp_service

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])

TEMPLATE_KEYS = ("invitation", "reminder", "thanks")


class SendRequest(BaseModel):
    phone_number: str
    message_text: str
    force_link: bool = False  # True => toujours retourner un lien wa.me


class BroadcastRequest(BaseModel):
    template: str = "reminder"           # invitation | reminder | thanks
    only_status: str | None = "pending"  # filtrer les invités par statut (None = tous)
    base_url: str = "http://localhost:5173"  # lien de l'invitation à inclure
    force_link: bool = False


def _render(template: str, name: str, base_url: str) -> str:
    if template == "invitation":
        return whatsapp_service.tpl_invitation(name, base_url)
    if template == "reminder":
        return whatsapp_service.tpl_reminder(name, base_url)
    if template == "thanks":
        return whatsapp_service.tpl_thanks(name)
    raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Modèle inconnu ({template})")


# ── PUBLIC : lien de remerciement après RSVP (l'invité envoie lui-même) ─────
@router.get("/confirm-link", summary="Lien WhatsApp de confirmation pour l'invité (public)")
def confirm_link(phone: str, name: str = "", message: str | None = None):
    """Génère un lien wa.me pré-rempli — l'invitation l'ouvre dans WhatsApp."""
    msg = message or whatsapp_service.tpl_thanks(name or "cher·e invité·e")
    return {"mode": "link", "link": whatsapp_service.build_link(phone, msg)}


# ── ADMIN : envoi unitaire ──────────────────────────────────────────────────
@router.post("/send", summary="Envoyer un message WhatsApp (admin)")
async def send_one(body: SendRequest, _admin=Depends(get_current_admin)):
    result = await whatsapp_service.send_message(body.phone_number, body.message_text, body.force_link)
    return result


@router.post("/preview", summary="Prévisualiser un modèle de message + lien (admin)")
def preview(template: str, phone: str, guest_name: str = "Cher·e invité·e", base_url: str = ""):
    message = _render(template, guest_name, base_url)
    return {
        "template": template,
        "message": message,
        "mode": "api" if settings.WHATSAPP_PHONE_ID and not settings.WHATSAPP_PHONE_ID.startswith("VOTRE_") else "link",
        "link": whatsapp_service.build_link(phone, message),
    }


# ── ADMIN : diffusion en masse ──────────────────────────────────────────────
@router.post("/broadcast", summary="Diffuser un modèle à tous les invités (admin)")
async def broadcast(body: BroadcastRequest, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    """Envoie (ou génère les liens pour) un message à chaque invité filtré par statut."""
    query = db.query(Guest)
    if body.only_status:
        query = query.filter(Guest.status == body.only_status)
    guests = query.all()
    if not guests:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Aucun invité correspondant")

    results = []
    for g in guests:
        name = f"{g.first_name} {g.last_name}".strip()
        phone = g.phone or ""
        if not phone:
            results.append({"guest": name, "skipped": "pas de numéro"})
            continue
        message = _render(body.template, name.split(" ")[0], body.base_url)
        outcome = await whatsapp_service.send_message(phone, message, body.force_link)
        results.append({"guest": name, **outcome})

    sent = sum(1 for r in results if r.get("success") and "skipped" not in r)
    return {"total": len(guests), "sent": sent, "mode": results[0].get("mode") if results else None, "results": results}
