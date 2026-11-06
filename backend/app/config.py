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

settings = Config()
