from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Inventory, UserRole
from schemas import InventoryCreate, InventoryRead
from auth import RoleChecker

router = APIRouter(prefix="/api/inventory", tags=["Inventory (Admin)"])
require_master_or_admin = RoleChecker([UserRole.MASTER, UserRole.ADMIN])

@router.post("/", response_model=InventoryRead, dependencies=[Depends(require_master_or_admin)])
def add_part(part_data: InventoryCreate, session: Session = Depends(get_session)):
    part = Inventory(**part_data.model_dump())
    session.add(part)
    session.commit()
    session.refresh(part)
    return part

@router.get("/", response_model=list[InventoryRead], dependencies=[Depends(RoleChecker([UserRole.MASTER, UserRole.ADMIN]))])
def get_inventory(session: Session = Depends(get_session)):
    return session.exec(select(Inventory)).all()

# НОВОЕ: Обновление запчасти
@router.patch("/{part_id}", response_model=InventoryRead, dependencies=[Depends(require_master_or_admin)])
def update_part(part_id: int, part_data: InventoryCreate, session: Session = Depends(get_session)):
    part = session.get(Inventory, part_id)
    if not part:
        raise HTTPException(404, "Part not found")
    
    part.name = part_data.name
    part.quantity = part_data.quantity
    part.price = part_data.price
    
    session.add(part)
    session.commit()
    session.refresh(part)
    return part

# НОВОЕ: Удаление запчасти
@router.delete("/{part_id}", dependencies=[Depends(require_master_or_admin)])
def delete_part(part_id: int, session: Session = Depends(get_session)):
    part = session.get(Inventory, part_id)
    if not part:
        raise HTTPException(404, "Part not found")
    
    session.delete(part)
    session.commit()
    return {"message": "Part deleted"}