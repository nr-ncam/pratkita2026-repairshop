from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from database import get_session
from models import RepairRequest, RequestStatus, User, UserRole, RequestPart
from auth import RoleChecker

router = APIRouter(prefix="/api/stats", tags=["Statistics"])
require_admin = RoleChecker([UserRole.ADMIN])

@router.get("/dashboard", dependencies=[Depends(require_admin)])
def get_dashboard_stats(session: Session = Depends(get_session)):
    """Gathers all data needed for the Admin Charts."""
    
    # 1. Заявки по статусам (Requests by status)
    status_counts = session.exec(
        select(RepairRequest.status, func.count(RepairRequest.id))
        .group_by(RepairRequest.status)
    ).all()
    requests_by_status = {status: count for status, count in status_counts}

    # 2. Доход (Revenue) - Assuming we sum service prices of issued/completed requests
    # In a real app, you'd also add the cost of parts used.
    revenue = session.exec(
        select(func.sum(RepairRequest.service_id)) # Simplified for now, we'll join Service later
        .where(RepairRequest.status == RequestStatus.ISSUED)
    ).first() or 0

    # 3. Популярные виды неисправностей (Popular device types)
    device_counts = session.exec(
        select(RepairRequest.device_type, func.count(RepairRequest.id))
        .group_by(RepairRequest.device_type)
        .order_by(func.count(RepairRequest.id).desc())
        .limit(5)
    ).all()
    popular_devices = {device: count for device, count in device_counts}

    # 4. Загрузка мастеров (Master Workload)
    master_workload = session.exec(
        select(User.full_name, func.count(RepairRequest.id))
        .join(RepairRequest, User.id == RepairRequest.master_id)
        .where(User.role == UserRole.MASTER)
        .group_by(User.full_name)
    ).all()
    
    return {
        "requests_by_status": requests_by_status,
        "revenue": revenue, # Note: Needs proper joining with Service table for real price
        "popular_devices": popular_devices,
        "master_workload": [{"name": name, "count": count} for name, count in master_workload]
    }