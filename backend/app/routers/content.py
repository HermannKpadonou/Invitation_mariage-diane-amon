"""Contenu éditable de l'invitation (admin)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Content
from app.schemas import ContentRead, ContentUpdate
from app.utils.auth import get_current_admin

router = APIRouter(prefix="/api/content", tags=["Contenu"])


@router.get("", response_model=list[ContentRead], summary="Tout le contenu (public)")
def get_content(db: Session = Depends(get_db)):
    return db.query(Content).all()


@router.get("/{section_key}", response_model=ContentRead, summary="Une section (public)")
def get_section(section_key: str, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.section_key == section_key).first()
    if content is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Section inconnue")
    return content


@router.patch("/{section_key}", response_model=ContentRead, summary="Modifier une section (admin)")
def update_section(section_key: str, body: ContentUpdate, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    content = db.query(Content).filter(Content.section_key == section_key).first()
    if content is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Section inconnue")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(content, key, value)
    db.commit()
    db.refresh(content)
    return content
