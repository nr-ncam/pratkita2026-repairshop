from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from database import get_session
from models import RepairRequest, User, UserRole, RequestStatus, Comment, Inventory, RequestPart
from schemas import StatusUpdate, CommentCreate, AddPart, CommentRead, RequestRead
from auth import RoleChecker

router = APIRouter(prefix="/api/master", tags=["Master Workspace"])
require_master = RoleChecker([UserRole.MASTER])

@router.get("/my-requests", response_model=List[RequestRead])
def get_my_assigned_requests(
    session: Session = Depends(get_session), 
    current_user: User = Depends(require_master)
):
    """Get only requests assigned to the logged-in master."""
    return session.exec(
        select(RepairRequest).where(RepairRequest.master_id == current_user.id)
    ).all()

@router.patch("/requests/{request_id}/status")
def update_status(
    request_id: int, 
    status_data: StatusUpdate, 
    session: Session = Depends(get_session), 
    current_user: User = Depends(require_master)
):
    """Change the status of a repair."""
    req = session.get(RepairRequest, request_id)
    if not req or req.master_id != current_user.id:
        raise HTTPException(403, "Not found or not assigned to you")
        
    req.status = status_data.status
    req.updated_at = datetime.utcnow()
    session.add(req)
    session.commit()
    return {"message": "Status updated successfully", "new_status": req.status}

@router.post("/requests/{request_id}/comments", response_model=CommentRead)
def add_comment(
    request_id: int,
    comment_data: CommentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_master)
):
    """Add a comment/report to the request."""
    req = session.get(RepairRequest, request_id)
    if not req or req.master_id != current_user.id:
        raise HTTPException(403, "Not found or not assigned to you")
        
    comment = Comment(
        text=comment_data.text,
        request_id=request_id,
        author_id=current_user.id
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment

@router.post("/requests/{request_id}/parts")
def use_part(
    request_id: int,
    part_data: AddPart,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_master)
):
    """Add a used part to the request and deduct from inventory."""
    req = session.get(RepairRequest, request_id)
    if not req or req.master_id != current_user.id:
        raise HTTPException(403, "Not found or not assigned to you")
        
    part = session.get(Inventory, part_data.part_id)
    if not part:
        raise HTTPException(404, "Part not found in inventory")
        
    if part.quantity < part_data.quantity:
        raise HTTPException(400, f"Not enough parts in stock. Available: {part.quantity}")
        
    # Deduct inventory
    part.quantity -= part_data.quantity
    session.add(part)
    
    # Save to request
    req_part = RequestPart(
        request_id=request_id,
        part_id=part_data.part_id,
        quantity=part_data.quantity,
        cost_at_time=part.price
    )
    session.add(req_part)
    session.commit()
    
    return {"message": f"Successfully added {part_data.quantity} of {part.name} to the request."}