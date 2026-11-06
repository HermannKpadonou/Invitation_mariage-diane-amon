from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

def _engine_kwargs():
    """SQLite : thread-check local. Postgres : vérification des connexions
    mortes (les bases managées coupent les connexions au repos)."""
    if settings.DATABASE_URL.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True, "pool_recycle": 280}

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app.models import AdminUser, Content, DotStep, EventInfo
    from app.utils.auth import hash_password
    import json
    
    # Création des tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Vérifier si l'admin existe déjà (pour ne pas re-seeder)
    admin_exists = db.query(AdminUser).filter(AdminUser.username == "admin").first()
    if admin_exists:
        db.close()
        return

    # Seed Admin User (identifiants issus de la config / du .env)
    admin = AdminUser(username=settings.ADMIN_USERNAME, password_hash=hash_password(settings.ADMIN_PASSWORD))
    db.add(admin)
    
    # Seed Content
    contents = [
        Content(section_key="hero", title="Diane & Amon", body_text="Nous sommes heureux de vous inviter à notre mariage.", metadata_json=json.dumps({"wedding_date": "2026-12-04", "venue": "Mairie de Port-Bouët & Pieu de Grand-Bassam"})),
        Content(section_key="couple_groom", title="Amon ALPHONSE", body_text="Futur époux, aimant et fidèle. (Bio de Amon)"),
        Content(section_key="couple_bride", title="Diane KPADONOU", body_text="Future épouse, créative et rayonnante. (Bio de Diane)"),
        Content(section_key="practical", title="Informations Pratiques", body_text="Cérémonie civile à 12h00 à la Mairie de Port-Bouët, cocktail 14h00 puis réception à 15h00 au Pieu de Grand-Bassam. Tenue de soirée."),
        Content(section_key="dresscode", title="Dress Code", body_text="Tenue de soirée — touches d'or champagne ou de vert émeraude. Blanc réservé à la mariée.")
    ]
    db.add_all(contents)
    
    # Seed DotSteps
    dot_steps = [
        DotStep(title="Présentation des Familles", description="Première rencontre officielle entre les deux familles.", step_order=1, is_completed=True),
        DotStep(title="Remise de la Dot", description="Cérémonie traditionnelle de la dot.", step_order=2, is_completed=True),
        DotStep(title="Bénédiction Traditionnelle", description="Bénédiction par les anciens.", step_order=3, is_completed=True)
    ]
    db.add_all(dot_steps)
    
    # Seed EventInfo
    events = [
        EventInfo(title="Cérémonie Civile", description="Union devant le maire.", event_date="2026-12-04", event_time="12:00", location_name="Mairie de Port-Bouët", location_address="Port-Bouët, Abidjan, Côte d'Ivoire", event_order=1),
        EventInfo(title="Cocktail", description="Accueil des invités sur le lieu de réception.", event_date="2026-12-04", event_time="14:00", location_name="Pieu de Grand-Bassam", location_address="Église de Jésus-Christ des saints des derniers jours, Grand-Bassam, Côte d'Ivoire", event_order=2),
        EventInfo(title="Réception", description="Honneurs, joie et famille.", event_date="2026-12-04", event_time="15:00", location_name="Pieu de Grand-Bassam", location_address="Église de Jésus-Christ des saints des derniers jours, Grand-Bassam, Côte d'Ivoire", event_order=3)
    ]
    db.add_all(events)
    
    # Aucun invité factice : la liste démarre vide en production.
    
    db.commit()
    db.close()
