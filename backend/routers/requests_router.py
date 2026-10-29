from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlmodel import Session, select
from typing import List, Optional
import shutil, os, uuid

from database import get_session
from models import RepairRequest, Service, UserRole, RequestStatus, User, Comment # Добавили Comment
from schemas import RequestRead, CommentRead # Добавили CommentRead
from auth import RoleChecker

router = APIRouter(prefix="/api/requests", tags=["Repair Requests"])

# Only Clients (and Admins if needed) can create requests
require_client = RoleChecker([UserRole.CLIENT, UserRole.ADMIN])

@router.post("/", status_code=201)
def create_request(
    device_type: str = Form(...),
    description: str = Form(...),
    service_id: int = Form(...),
    photo: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_client)
):
    """Client endpoint to create a new repair request with an optional photo."""
    
    # 1. Validate that the service exists
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # 2. Handle the photo upload
    photo_path = None
    if photo:
        # Validate file type (basic security)
        if not photo.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
            
        # Generate unique filename to prevent overwriting
        file_extension = os.path.splitext(photo.filename)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        photo_path = f"media/{filename}"
        
        os.makedirs("media", exist_ok=True)
        with open(photo_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

    # 3. Create the DB record
    db_request = RepairRequest(
        device_type=device_type,
        description=description,
        service_id=service_id,
        client_id=current_user.id,
        photo_path=photo_path,
        status=RequestStatus.ACCEPTED # Automatically sets to "Принята"
    )
    
    session.add(db_request)
    session.commit()
    session.refresh(db_request)
    
    return {"message": "Заявка успешно создана", "request_id": db_request.id}


@router.get("/my", response_model=List[RequestRead])
def get_my_requests(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_client)
):
    requests = session.exec(select(RepairRequest).where(RepairRequest.client_id == current_user.id)).all()
    
    result = []
    for req in requests:
        service = session.get(Service, req.service_id)
        
        # ИСПРАВЛЕНИЕ: Подтягиваем комментарии мастера к заявке
        comments = session.exec(select(Comment).where(Comment.request_id == req.id)).all()
        comments_data = [CommentRead.model_validate(c) for c in comments] # или .model_dump()

        req_dict = req.model_dump()
        req_dict["service_name"] = service.name if service else "Unknown"
        req_dict["comments"] = comments_data # <--- ДОБАВЛЕНО
        
        if req.photo_path:
             req_dict["photo_path"] = f"/{req.photo_path}"
             
        result.append(req_dict)
        
    return result