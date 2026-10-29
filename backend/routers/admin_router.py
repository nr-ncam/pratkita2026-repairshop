from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import RepairRequest, User, UserRole
from auth import RoleChecker
from typing import List
from schemas import UserRead

router = APIRouter(prefix="/api/admin", tags=["Admin Panel"])
require_admin = RoleChecker([UserRole.ADMIN])

@router.get("/requests")
def get_all_requests(session: Session = Depends(get_session), current_user: User = Depends(require_admin)):
    """View all requests to manage them."""
    return session.exec(select(RepairRequest)).all()

@router.get("/users", response_model=List[UserRead])
def get_all_users(session: Session = Depends(get_session), current_user: User = Depends(require_admin)):
    """View all registered users."""
    return session.exec(select(User)).all()

@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int, 
    new_role: UserRole, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(require_admin)
):
    """Change a user's role (e.g., promote client to master)."""
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    # Защита: чтобы админ случайно не снял роль с самого себя
    if user.id == current_user.id:
        raise HTTPException(400, "You cannot change your own role")

    user.role = new_role
    session.add(user)
    session.commit()
    return {"message": f"User {user.email} role updated to {new_role}"}

@router.put("/requests/{request_id}/assign/{master_id}")
def assign_master(
    request_id: int, 
    master_id: int, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(require_admin)
):
    """Assign a specific request to a specific master."""
    req = session.get(RepairRequest, request_id)
    if not req:
        raise HTTPException(404, "Request not found")
        
    master = session.get(User, master_id)
    if not master or master.role != UserRole.MASTER:
        raise HTTPException(400, "Invalid master ID")

    req.master_id = master_id
    session.add(req)
    session.commit()
    return {"message": f"Request {request_id} assigned to master {master.full_name}"}

@router.get("/masters")
def get_all_masters(session: Session = Depends(get_session), current_user: User = Depends(require_admin)):
    """Get a list of all users with the MASTER role."""
    masters = session.exec(select(User).where(User.role == UserRole.MASTER)).all()
    return [{"id": m.id, "full_name": m.full_name} for m in masters]
