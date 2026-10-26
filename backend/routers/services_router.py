from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Service, UserRole
from schemas import ServiceCreate, ServiceRead
from auth import RoleChecker

router = APIRouter(prefix="/api/services", tags=["Services"])

# Only Admins can create services
require_admin = RoleChecker([UserRole.ADMIN])

@router.post("/", response_model=ServiceRead, dependencies=[Depends(require_admin)])
def create_service(service_data: ServiceCreate, session: Session = Depends(get_session)):
    """Admin endpoint to add a new service to the catalog."""
    db_service = Service(**service_data.model_dump())
    session.add(db_service)
    session.commit()
    session.refresh(db_service)
    return db_service

@router.get("/", response_model=list[ServiceRead])
def get_services(session: Session = Depends(get_session)):
    """Public endpoint to view the catalog."""
    services = session.exec(select(Service)).all()
    return services