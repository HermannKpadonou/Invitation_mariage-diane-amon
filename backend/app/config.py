import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Paramètres par défaut de la base de données et JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "wedding-secret-key-change-in-production")
    DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./wedding.db"
    # Render / Neon / Supabase donnent parfois « postgres:// » — SQLAlchemy exige « postgresql:// »
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24h

    # Compte admin par défaut (seed) — CHANGEZ-LES en production via .env
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "mariage2026")

    # Configuration WhatsApp Cloud API (Meta) — optionnelle.
    # Sans ces clés, l'API fonctionne en mode « lien wa.me » (gratuit, sans compte).
    # .env : WHATSAPP_PHONE_ID=1234567890  WHATSAPP_API_TOKEN=EAAG...
    WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
    WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "")
    WHATSAPP_API_URL = os.getenv(
        "WHATSAPP_API_URL",
        "https://graph.facebook.com/v19.0/{PHONE_ID}/messages" if WHATSAPP_PHONE_ID else ""
    )

    # CORS : ouvert aux invités qui consultent l'invitation depuis n'importe quel
    # hébergement (fichier local, Netlify, GitHub Pages…). Les endpoints sensibles
    # exigent de toute façon un JWT admin.
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # ── Notifications des mariés (RSVP, livre d'or, visites) ─────────────
    # Email : SMTP — avec Gmail, créez un mot de passe d'application sur
    # https://myaccount.google.com/apppasswords puis :
    #   SMTP_HOST=smtp.gmail.com   SMTP_PORT=587   SMTP_USER=vous@gmail.com
    NOTIFY_EMAIL_TO = os.getenv("NOTIFY_EMAIL_TO", "hmkpadonou@gmail.com")
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    # WhatsApp (gratuit) via CallMeBot : sur le téléphone des mariés, ajoutez le
    # numéro du bot indiqué sur https://www.callmebot.com/whatsapp.php aux
    # contacts, envoyez-lui « I allow callmebot to send me messages », attendez
    # l'apikey, puis définissez CALLMEBOT_APIKEY sur Render.
    NOTIFY_WHATSAPP_TO = os.getenv("NOTIFY_WHATSAPP_TO", "+2250757677707")
    CALLMEBOT_APIKEY = os.getenv("CALLMEBOT_APIKEY", "")
    # Visites : au plus une notification toutes les VISIT_NOTIFY_MINUTES minutes.
    VISIT_NOTIFY_MINUTES = int(os.getenv("VISIT_NOTIFY_MINUTES", "15"))
    # Adresse publique du site (pour les liens dans les emails) — renseignée
    # automatiquement côté invitation via PUBLIC_BASE_URL, sinon à définir.
    PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "")

settings = Config()
