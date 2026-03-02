from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Incident, User, IncidentStatus, Severity
from app.schemas import IncidentCreate, IncidentUpdate, IncidentResponse
from app.auth import get_current_user, log_audit

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.get("", response_model=List[IncidentResponse])
async def list_incidents(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[IncidentStatus] = None,
    severity_filter: Optional[Severity] = None,
    model_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all incidents with optional filters"""
    query = db.query(Incident)
    
    if status_filter:
        query = query.filter(Incident.status == status_filter)
    
    if severity_filter:
        query = query.filter(Incident.severity == severity_filter)
    
    if model_id:
        query = query.filter(Incident.model_id == model_id)
    
    incidents = query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()
    return [IncidentResponse.model_validate(i) for i in incidents]


@router.get("/stats", response_model=dict)
async def get_incident_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get incident statistics"""
    total_incidents = db.query(func.count(Incident.id)).scalar()
    
    open_incidents = db.query(func.count(Incident.id)).filter(
        Incident.status.in_([IncidentStatus.open, IncidentStatus.investigating])
    ).scalar()
    
    by_severity = db.query(
        Incident.severity,
        func.count(Incident.id)
    ).group_by(Incident.severity).all()
    
    by_type = db.query(
        Incident.type,
        func.count(Incident.id)
    ).group_by(Incident.type).all()
    
    by_status = db.query(
        Incident.status,
        func.count(Incident.id)
    ).group_by(Incident.status).all()
    
    return {
        "total": total_incidents,
        "open": open_incidents,
        "by_severity": {str(sev): count for sev, count in by_severity},
        "by_type": {str(typ): count for typ, count in by_type},
        "by_status": {str(stat): count for stat, count in by_status}
    }


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific incident by ID"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    return IncidentResponse.model_validate(incident)


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new incident"""
    new_incident = Incident(
        **incident_data.model_dump(),
        reported_by=current_user.id,
        status=IncidentStatus.open
    )
    
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="create",
        resource_type="incident",
        resource_id=new_incident.id,
        details={"title": new_incident.title, "severity": str(new_incident.severity)}
    )
    
    return IncidentResponse.model_validate(new_incident)


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    incident_data: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Update fields
    update_data = incident_data.model_dump(exclude_unset=True)
    
    # If status is being changed to resolved/closed, set resolved_at
    if "status" in update_data and update_data["status"] in [IncidentStatus.resolved, IncidentStatus.closed]:
        if incident.resolved_at is None:
            incident.resolved_at = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(incident, field, value)
    
    db.commit()
    db.refresh(incident)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="update",
        resource_type="incident",
        resource_id=incident.id,
        details={"updated_fields": list(update_data.keys())}
    )
    
    return IncidentResponse.model_validate(incident)


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an incident"""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    # Log audit before deleting
    log_audit(
        db=db,
        user_id=current_user.id,
        action="delete",
        resource_type="incident",
        resource_id=incident.id,
        details={"title": incident.title}
    )
    
    db.delete(incident)
    db.commit()
    
    return None
