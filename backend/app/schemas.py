from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# --- Guest Schemas ---
class GuestBase(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    status: str = "pending"
    companions_count: int = 0
    dietary_options: Optional[str] = None
    transport_needs: bool = False
    notes: Optional[str] = None

class RSVPCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = ""   # optionnel : l'invitation envoie le nom complet dans first_name
    phone: str
    status: str
    companions_count: int = 0
    dietary_options: Optional[str] = None
    transport_needs: bool = False

class GuestCreate(GuestBase):
    pass

# --- Guestbook (livre d'or) ---
class GuestbookCreate(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    message: str = Field(min_length=2, max_length=280)

class GuestbookRead(BaseModel):
    id: int
    name: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

class GuestUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
    companions_count: Optional[int] = None
    dietary_options: Optional[str] = None
    transport_needs: Optional[bool] = None
    notes: Optional[str] = None

class GuestRead(GuestBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Content Schemas ---
class ContentBase(BaseModel):
    title: Optional[str] = None
    body_text: Optional[str] = None
    image_urls: Optional[str] = None
    metadata_json: Optional[str] = None

class ContentUpdate(ContentBase):
    pass

class ContentRead(ContentBase):
    id: int
    section_key: str
    updated_at: datetime

    class Config:
        from_attributes = True

# --- DotStep Schemas ---
class DotStepBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    step_order: int = 0
    is_completed: bool = True

class DotStepCreate(DotStepBase):
    pass

class DotStepUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    step_order: Optional[int] = None
    is_completed: Optional[bool] = None

class DotStepRead(DotStepBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- EventInfo Schemas ---
class EventInfoBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: Optional[str] = None
    event_time: Optional[str] = None
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    maps_url: Optional[str] = None
    image_url: Optional[str] = None
    event_order: int = 0

class EventInfoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[str] = None
    event_time: Optional[str] = None
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    maps_url: Optional[str] = None
    image_url: Optional[str] = None
    event_order: Optional[int] = None

class EventInfoRead(EventInfoBase):
    id: int

    class Config:
        from_attributes = True

# --- Auth Schemas ---
class LoginRequest(BaseModel):
    username: str
    password: str

class ChangePasswordRequest(BaseModel):
    ancien: str
    nouveau: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class AdminUserRead(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

# --- Stats Schemas ---
class StatsResponse(BaseModel):
    total_guests: int
    total_present: int
    total_absent: int
    total_pending: int
    total_companions: int

# --- WhatsApp Schemas ---
class WhatsAppMessage(BaseModel):
    phone_number: str
    message_text: str
