from pydantic import BaseModel, EmailStr
from typing import Optional
from models import UserRole

# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str
    role: UserRole = UserRole.CLIENT # Default to client

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str
    role: UserRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# --- TOKEN SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Append these to backend/schemas.py
from datetime import datetime
from models import RequestStatus

# --- SERVICE SCHEMAS ---
class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ServiceRead(ServiceCreate):
    id: int

# --- REPAIR REQUEST SCHEMAS ---
class RequestRead(BaseModel):
    id: int
    device_type: str
    description: str
    photo_path: Optional[str] = None
    status: RequestStatus
    created_at: datetime
    service_id: int
    client_id: int
    
    # We will manually add the service name in the route for a nicer UI
    service_name: Optional[str] = None 

# Append to backend/schemas.py
from typing import List

# --- INVENTORY SCHEMAS ---
class InventoryCreate(BaseModel):
    name: str
    quantity: int
    price: float

class InventoryRead(InventoryCreate):
    id: int

# --- COMMENT SCHEMAS ---
class CommentCreate(BaseModel):
    text: str

class CommentRead(BaseModel):
    id: int
    text: str
    created_at: datetime
    author_id: int

# --- MASTER WORKSPACE SCHEMAS ---
class StatusUpdate(BaseModel):
    status: RequestStatus

class AddPart(BaseModel):
    part_id: int
    quantity: int = 1