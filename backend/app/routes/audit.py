from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import AuditLog, User
from app.schemas import AuditLogResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=List[AuditLogResponse])
async def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List audit logs with optional filters (read-only)"""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    
    if resource_id is not None:
        query = query.filter(AuditLog.resource_id == resource_id)
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get("/recent", response_model=List[AuditLogResponse])
async def get_recent_audit_logs(
    limit: int = Query(default=10, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get most recent audit log entries"""
    logs = db.query(AuditLog).order_by(
        AuditLog.created_at.desc()
    ).limit(limit).all()
    
    return [AuditLogResponse.model_validate(log) for log in logs]
