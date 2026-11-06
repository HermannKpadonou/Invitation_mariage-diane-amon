"""Service WhatsApp — deux modes :

1. **Cloud API (Meta)** — si WHATSAPP_PHONE_ID + WHATSAPP_API_TOKEN sont définis
   dans le fichier .env, l'envoi est réel via l'API officielle.
2. **Mode lien (wa.me)** — sinon, génération de liens de clic-à-envoyer,
   utilisables gratuitement depuis le téléphone des mariés (aucune clé requise).
"""
import logging
import re
import urllib.parse

import httpx

from app.config import settings

logger = logging.getLogger("whatsapp")

WA_BASE = "https://wa.me/"


def normalize_phone(phone: str) -> str:
    """Nettoie un numéro : garde uniquement les chiffres (format international attendu).

    Ex. '+225 07 07 07 07 07' -> '2250707070707'. Convertit aussi le format
    local ivoirien '07xxxxxxxx' (10 chiffres) en '22507xxxxxxxx'.
    """
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 10 and digits.startswith(("01", "05", "07")):  # format local CI
        digits = "225" + digits
    return digits


def build_link(phone: str, message: str) -> str:
    """Lien wa.me clic-à-envoyer (mode sans clé API)."""
    return f"{WA_BASE}{normalize_phone(phone)}?text={urllib.parse.quote(message)}"


# ── Modèles de messages (personnalisables) ──────────────────────────────────
def tpl_invitation(guest_name: str, base_url: str) -> str:
    return (
        f"Bonjour {guest_name} 🌿\n\n"
        f"C'est avec une immense joie que nous vous invitons au mariage de "
        f"Diane KPADONOU & Amon ALPHONSE 💍\n"
        f"📅 Vendredi 4 décembre 2026 — Mairie de Port-Bouët (10h00), réception au Pieu de Grand-Bassam.\n\n"
        f"Votre invitation & confirmation de présence ici :\n{base_url}\n\n"
        f"Dress code : tenue de soirée 👑\n"
        f"#DianeEtAmon2026"
    )


def tpl_reminder(guest_name: str, base_url: str) -> str:
    return (
        f"Bonjour {guest_name} 🤍\n\n"
        f"Petit rappel : il nous manque encore votre réponse pour le mariage de "
        f"Diane & Amon (4 décembre 2026) 🙏\n"
        f"Merci de confirmer avant le 20 novembre :\n{base_url}\n\n"
        f"Nous comptons sur vous !"
    )


def tpl_thanks(guest_name: str) -> str:
    return (
        f"Merci {guest_name} 🧡\n\n"
        f"Votre réponse a bien été reçue — nous sommes honorés de vous compter parmi nous.\n"
        f"À très vite pour célébrer l'union de Diane & Amon !\n"
        f"#DianeEtAmon2026"
    )


async def send_via_api(phone: str, message: str) -> dict:
    """Envoi réel via WhatsApp Cloud API (Meta). Lève une exception si non configuré."""
    if not settings.WHATSAPP_PHONE_ID or settings.WHATSAPP_PHONE_ID.startswith("VOTRE_"):
        raise RuntimeError("WhatsApp Cloud API non configurée (WHATSAPP_PHONE_ID manquant)")
    url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": normalize_phone(phone),
        "type": "text",
        "text": {"preview_url": True, "body": message},
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload, headers=headers)
        ok = resp.status_code < 300
        if not ok:
            logger.error("WhatsApp API %s : %s", resp.status_code, resp.text)
        return {"success": ok, "status": resp.status_code, "detail": resp.text[:300]}


async def send_message(phone: str, message: str, force_link: bool = False) -> dict:
    """Envoie via l'API si configurée, sinon retombe sur le mode lien.

    Réponse normalisée : {mode, success, phone, link?, detail?}
    """
    if force_link:
        return {"mode": "link", "success": True, "phone": normalize_phone(phone), "link": build_link(phone, message)}
    try:
        result = await send_via_api(phone, message)
        return {"mode": "api", "phone": normalize_phone(phone), **result}
    except RuntimeError:
        return {"mode": "link", "success": True, "phone": normalize_phone(phone), "link": build_link(phone, message)}
    except httpx.HTTPError as exc:
        logger.exception("Échec réseau WhatsApp, bascule en mode lien")
        return {"mode": "link", "success": True, "phone": normalize_phone(phone), "link": build_link(phone, message), "detail": str(exc)}
