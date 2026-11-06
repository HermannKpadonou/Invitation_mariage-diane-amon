from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routers import auth, guests, content, stats, whatsapp, guestbook

app = FastAPI(
    title="API Mariage Diane & Amon",
    description=(
        "Backend de la plateforme d'invitation — réception des RSVP, gestion des invités, "
        "statistiques et envoi de messages WhatsApp (Cloud API Meta ou liens wa.me)."
    ),
    version="2.0.0"
)

# Configuration CORS — ouvert aux visiteurs de l'invitation (hébergée n'importe où) ;
# les endpoints d'administration restent protégés par JWT.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=".*",   # file:// (Origin: null), Netlify, GitHub Pages…
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routeurs
app.include_router(auth.router)
app.include_router(guests.router)
app.include_router(content.router)
app.include_router(stats.router)
app.include_router(whatsapp.router)
app.include_router(guestbook.router)

# ── Service de l'invitation et du tableau de bord ────────────────────────────
# http://127.0.0.1:8010/          → index.html  (l'invitation)
# http://127.0.0.1:8010/admin.html → tableau de bord admin
# http://127.0.0.1:8010/assets/…  → photos
# Indispensable pour la musique YouTube : un lecteur intégré ne fonctionne
# que depuis une origine HTTP (un fichier ouvert en file:// est bloqué par YouTube).
from pathlib import Path as _Path
from fastapi.staticfiles import StaticFiles as _StaticFiles
_PROJECT_ROOT = _Path(__file__).resolve().parents[2]
app.mount("/", _StaticFiles(directory=_PROJECT_ROOT, html=True), name="site")

@app.on_event("startup")
def on_startup():
    """Exécuté au démarrage de l'application."""
    # Initialisation de la base de données et seeding si nécessaire
    init_db()

@app.get("/", tags=["Root"], include_in_schema=False)
def root():
    """Sert l'invitation directement — la musique YouTube exige une origine HTTP."""
    from fastapi.responses import FileResponse
    return FileResponse(_PROJECT_ROOT / "index.html")
