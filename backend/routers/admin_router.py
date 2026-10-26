from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import RepairRequest, User, UserRole
from auth import RoleChecker

router = APIRouter(prefix="/api/admin", tags=["Admin Panel"])
require_admin = RoleChecker([UserRole.ADMIN])

@router.get("/requests")
def get_all_requests(session: Session = Depends(get_session), current_user: User = Depends(require_admin)):
    """View all requests to manage them."""
    return session.exec(select(RepairRequest)).all()

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