from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship

# --- ENUMS ---
class UserRole(str, Enum):
    CLIENT = "client"
    MASTER = "master"
    ADMIN = "admin"

class RequestStatus(str, Enum):
    ACCEPTED = "Принята"
    DIAGNOSTICS = "В диагностике"
    REPAIRING = "В ремонте"
    READY = "Готова к выдаче"
    ISSUED = "Выдана"

# --- MODELS ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: str
    phone: str
    role: UserRole = Field(default=UserRole.CLIENT)
    
    # Relationships
    client_requests: List["RepairRequest"] = Relationship(back_populates="client", sa_relationship_kwargs={"foreign_keys": "[RepairRequest.client_id]"})
    master_requests: List["RepairRequest"] = Relationship(back_populates="master", sa_relationship_kwargs={"foreign_keys": "[RepairRequest.master_id]"})

class Service(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    price: float
    
class Inventory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    quantity: int = Field(default=0)
    price: float

class RepairRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_type: str
    description: str
    photo_path: Optional[str] = None
    status: RequestStatus = Field(default=RequestStatus.ACCEPTED)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    client_id: int = Field(foreign_key="user.id")
    master_id: Optional[int] = Field(default=None, foreign_key="user.id")
    service_id: int = Field(foreign_key="service.id")
    
    # Relationships
    client: Optional[User] = Relationship(back_populates="client_requests", sa_relationship_kwargs={"foreign_keys": "[RepairRequest.client_id]"})
    master: Optional[User] = Relationship(back_populates="master_requests", sa_relationship_kwargs={"foreign_keys": "[RepairRequest.master_id]"})
    comments: List["Comment"] = Relationship(back_populates="request")

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    request_id: int = Field(foreign_key="repairrequest.id")
    author_id: int = Field(foreign_key="user.id")
    
    request: Optional[RepairRequest] = Relationship(back_populates="comments")
    # Note: Author relationship omitted for brevity, but we will need it later to show names.

class RequestPart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quantity: int = 1
    cost_at_time: float # Save the price at the time of repair
    
    request_id: int = Field(foreign_key="repairrequest.id")
    part_id: int = Field(foreign_key="inventory.id")