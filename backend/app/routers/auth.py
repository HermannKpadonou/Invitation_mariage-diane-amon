"""Authentification admin (JWT)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import AdminUser
from app.schemas import ChangePasswordRequest, LoginRequest, TokenResponse
from app.utils.auth import create_access_token, get_current_admin, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse, summary="Connexion admin")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.username == body.username).first()
    if not admin or not verify_password(body.password, admin.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants incorrects")
    return TokenResponse(access_token=create_access_token(admin.username), token_type="bearer")


@router.post("/change-password", summary="Changer le mot de passe admin")
def change_password(
    body: ChangePasswordRequest,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Appliqué immédiatement — aucun redémarrage ni recréation de base requis."""
    if not verify_password(body.ancien, admin.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ancien mot de passe incorrect")
    if len(body.nouveau) < 8:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Le nouveau mot de passe doit faire au moins 8 caractères")
    admin.password_hash = hash_password(body.nouveau)
    db.commit()
    return {"message": "Mot de passe mis à jour"}
