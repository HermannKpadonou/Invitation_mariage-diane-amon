"""Notifications des mariés (email + WhatsApp) à chaque interaction.

Événements notifiés :
- RSVP : un invité confirme (ou modifie) sa réponse ;
- Livre d'or : un invité publie un mot doux ;
- Visites : consultations de l'invitation (AGRÉGÉES — au plus un message
  toutes les VISIT_NOTIFY_MINUTES minutes, sinon les mariés seraient
  notifiés à chaque rafraîchissement de page).

Canaux (tous optionnels — configurés via variables d'environnement) :
- Email    : API HTTP Brevo (recommandé sur Render gratuit, qui BLOQUE les
             ports SMTP 25/465/587) ou SMTP classique (Gmail…)
- WhatsApp : CallMeBot (gratuit, apikey personnelle) ou Cloud API Meta

Chaque envoi est « fire-and-forget » : une panne de notification ne doit
JAMAIS empêcher un invité de répondre ou d'écrire un message.
"""
import asyncio
import logging
import smtplib
import time
from email.message import EmailMessage
from urllib.parse import quote

import httpx

from app.config import settings

logger = logging.getLogger("notify")

STATUT_FR = {"present": "Présent·e ✅", "absent": "Absent·e ❌", "pending": "En attente ⏳"}


# ── Canaux ──────────────────────────────────────────────────────────────────
def _smtp_send(msg: EmailMessage) -> None:
    """Blocant (exécuté dans un thread séparé)."""
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as s:
        s.starttls()
        s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        s.send_message(msg)


async def _send_email_brevo(subject: str, body: str) -> None:
    """Envoi via l'API HTTP Brevo (https, port 443) — contourne le blocage
    des ports SMTP qu'imposent les hébergeurs gratuits (Render…)."""
    payload = {
        "sender": {"name": "Invitation Diane & Amon", "email": settings.SMTP_USER or settings.NOTIFY_EMAIL_TO},
        "to": [{"email": settings.NOTIFY_EMAIL_TO}],
        "subject": subject,
        "textContent": body,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            "https://api.brevo.com/v3/smtp-email",
            json=payload,
            headers={"api-key": settings.BREVO_API_KEY, "accept": "application/json"},
        )
        r.raise_for_status()
    logger.info("Email envoyé via Brevo à %s : %s", settings.NOTIFY_EMAIL_TO, subject)


async def _send_email(subject: str, body: str) -> None:
    # Priorité à Brevo (API HTTP) — fonctionne même quand les ports SMTP
    # sont bloqués par l'hébergeur (Render gratuit).
    if settings.BREVO_API_KEY:
        await _send_email_brevo(subject, body)
        return
    if not (settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD):
        logger.info("Email non envoyé (Brevo/SMTP non configuré) : %s", subject)
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_USER
    msg["To"] = settings.NOTIFY_EMAIL_TO
    msg.set_content(body)
    await asyncio.to_thread(_smtp_send, msg)
    logger.info("Email envoyé à %s : %s", settings.NOTIFY_EMAIL_TO, subject)


async def _send_whatsapp(text: str) -> None:
    if settings.CALLMEBOT_APIKEY:
        url = (
            "https://api.callmebot.com/whatsapp.php?phone="
            + quote(settings.NOTIFY_WHATSAPP_TO)
            + "&text=" + quote(text)
            + "&apikey=" + quote(settings.CALLMEBOT_APIKEY)
        )
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
            r.raise_for_status()
        logger.info("WhatsApp envoyé à %s", settings.NOTIFY_WHATSAPP_TO)
        return
    logger.info("WhatsApp non envoyé (CallMeBot non configuré) : %s", text[:60])


async def _notify_all(subject: str, body: str) -> None:
    """Envoie sur tous les canaux configurés ; n'échoue jamais bruyamment."""
    results = await asyncio.gather(
        _send_email(subject, body), _send_whatsapp(body), return_exceptions=True
    )
    for r in results:
        if isinstance(r, Exception):
            logger.warning("Notification échouée : %s", r)


# ── Événements ──────────────────────────────────────────────────────────────
async def notify_rsvp(name: str, status: str, companions: int, is_new: bool) -> None:
    emoji = "💍" if is_new else "🔁"
    sujet = f"RSVP — {name} : {STATUT_FR.get(status, status)}"
    corps = (
        f"{emoji} {'Nouvelle réponse' if is_new else 'Réponse mise à jour'} sur l'invitation !\n\n"
        f"Invité : {name}\n"
        f"Réponse : {STATUT_FR.get(status, status)}\n"
        f"Accompagnants : {companions}\n\n"
        f"Détails dans le tableau de bord : {settings.PUBLIC_BASE_URL or ''}/admin.html\n"
        f"— Invitation Diane & Amon 🤍"
    )
    await _notify_all(sujet, corps)


async def notify_guestbook(name: str, message: str) -> None:
    sujet = f"Livre d'or — message de {name}"
    corps = (
        f"📝 Nouveau mot doux sur l'invitation !\n\n"
        f"{name} a écrit :\n\n« {message} »\n\n"
        f"À lire dans le livre d'or ou le tableau de bord.\n"
        f"— Invitation Diane & Amon 🤍"
    )
    await _notify_all(sujet, corps)


# ── Visites (agrégées) ──────────────────────────────────────────────────────
_state = {"visits": 0, "last": 0.0}


async def notify_visit() -> None:
    """Comptabilise une visite ; notifie au plus 1 fois / VISIT_NOTIFY_MINUTES.

    Appelé depuis un endpoint async (event loop unique) : le compteur est
    modifié sans await intermédiaire → pas de course possible.
    """
    now = time.time()
    _state["visits"] += 1
    if now - _state["last"] < settings.VISIT_NOTIFY_MINUTES * 60:
        return
    n = _state["visits"]
    _state["visits"] = 0
    _state["last"] = now
    sujet = f"👀 Invitation — {n} visite(s)"
    corps = (
        f"{n} visite(s) de l'invitation depuis le dernier point "
        f"(regroupées toutes les {settings.VISIT_NOTIFY_MINUTES} minutes).\n\n"
        f"— Invitation Diane & Amon 🤍"
    )
    await _notify_all(sujet, corps)
