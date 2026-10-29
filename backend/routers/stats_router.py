# backend/routers/stats.py
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from database import get_session
from models import RepairRequest, RequestStatus, User, UserRole, Service # Добавили Service
from auth import RoleChecker

router = APIRouter(prefix="/api/stats", tags=["Statistics"])
require_admin = RoleChecker([UserRole.ADMIN])

@router.get("/dashboard", dependencies=[Depends(require_admin)])
def get_dashboard_stats(session: Session = Depends(get_session)):
    
    status_counts = session.exec(
        select(RepairRequest.status, func.count(RepairRequest.id))
        .group_by(RepairRequest.status)
    ).all()
    requests_by_status = {status: count for status, count in status_counts}

    # ИСПРАВЛЕНИЕ: Реальная выручка (Джойн с таблицей Service)
    revenue = session.exec(
        select(func.sum(Service.price))
        .join(RepairRequest, RepairRequest.service_id == Service.id)
        .where(RepairRequest.status == RequestStatus.ISSUED)
    ).first() or 0.0

    # НОВОЕ (по ТЗ): Доход по месяцам (работает для SQLite)
    revenue_by_month = session.exec(
        select(
            func.strftime('%Y-%m', RepairRequest.created_at).label('month'),
            func.sum(Service.price)
        )
        .join(Service, RepairRequest.service_id == Service.id)
        .where(RepairRequest.status == RequestStatus.ISSUED)
        .group_by('month')
        .order_by('month')
    ).all()
    # Форматируем в словарь {"2023-10": 15000, "2023-11": 20000}
    revenue_monthly = {month: float(amount) for month, amount in revenue_by_month}

    device_counts = session.exec(
        select(RepairRequest.device_type, func.count(RepairRequest.id))
        .group_by(RepairRequest.device_type)
        .order_by(func.count(RepairRequest.id).desc())
        .limit(5)
    ).all()
    popular_devices = {device: count for device, count in device_counts}

    master_workload = session.exec(
        select(User.full_name, func.count(RepairRequest.id))
        .join(RepairRequest, User.id == RepairRequest.master_id)
        .where(User.role == UserRole.MASTER)
        .group_by(User.full_name)
    ).all()
    
    return {
        "requests_by_status": requests_by_status,
        "revenue": revenue,
        "revenue_by_month": revenue_monthly, # <--- ДОБАВЛЕНО
        "popular_devices": popular_devices,
        "master_workload": [{"name": name, "count": count} for name, count in master_workload]
    }