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
    db_service = Service(**service_data.model_dump())
    session.add(db_service)
    session.commit()
    session.refresh(db_service)
    return db_service

@router.get("/", response_model=list[ServiceRead])
def get_services(session: Session = Depends(get_session)):
    return session.exec(select(Service)).all()

# НОВОЕ: Обновление услуги
@router.patch("/{service_id}", response_model=ServiceRead, dependencies=[Depends(require_admin)])
def update_service(service_id: int, service_data: ServiceCreate, session: Session = Depends(get_session)):
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(404, "Service not found")
    
    service.name = service_data.name
    service.price = service_data.price
    service.description = service_data.description
    
    session.add(service)
    session.commit()
    session.refresh(service)
    return service

# НОВОЕ: Удаление услуги
@router.delete("/{service_id}", dependencies=[Depends(require_admin)])
def delete_service(service_id: int, session: Session = Depends(get_session)):
    service = session.get(Service, service_id)
    if not service:
        raise HTTPException(404, "Service not found")
    
    session.delete(service)
    session.commit()
    return {"message": "Service deleted"}