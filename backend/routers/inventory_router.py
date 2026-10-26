from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Inventory, UserRole
from schemas import InventoryCreate, InventoryRead
from auth import RoleChecker

router = APIRouter(prefix="/api/inventory", tags=["Inventory (Admin)"])
require_admin = RoleChecker([UserRole.ADMIN])

@router.post("/", response_model=InventoryRead, dependencies=[Depends(require_admin)])
def add_part(part_data: InventoryCreate, session: Session = Depends(get_session)):
    part = Inventory(**part_data.model_dump())
    session.add(part)
    session.commit()
    session.refresh(part)
    return part

@router.get("/", response_model=list[InventoryRead])
def get_inventory(session: Session = Depends(get_session)):
    # Masters and Admins can see inventory
    return session.exec(select(Inventory)).all()