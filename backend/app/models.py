from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Guest(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    status = Column(String, default="pending")  # 'present', 'absent', 'pending'
    companions_count = Column(Integer, default=0)
    dietary_options = Column(String, nullable=True)  # ex: 'vegetarien', 'halal', 'sans_gluten'
    transport_needs = Column(Boolean, default=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    section_key = Column(String, unique=True, nullable=False, index=True)  # 'hero', 'couple_groom', 'couple_bride', 'practical', 'dresscode'
    title = Column(String, nullable=True)
    body_text = Column(Text, nullable=True)
    image_urls = Column(Text, nullable=True)  # JSON string of list
    metadata_json = Column(Text, nullable=True)  # JSON string for extra data
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class DotStep(Base):
    __tablename__ = "dot_steps"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    step_order = Column(Integer, default=0)
    is_completed = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EventInfo(Base):
    __tablename__ = "event_infos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(String, nullable=True)
    event_time = Column(String, nullable=True)
    location_name = Column(String, nullable=True)
    location_address = Column(String, nullable=True)
    maps_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    event_order = Column(Integer, default=0)

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

class GuestbookEntry(Base):
    __tablename__ = "guestbook"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
