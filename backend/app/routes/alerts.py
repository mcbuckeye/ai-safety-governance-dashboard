from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import Alert, User, AlertStatus, Model, Incident
from app.schemas import AlertCreate, AlertUpdate, AlertResponse
from app.auth import get_current_user, log_audit

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[AlertStatus] = None,
    model_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all alerts with optional filters"""
    query = db.query(Alert)
    
    if status_filter:
        query = query.filter(Alert.status == status_filter)
    
    if model_id:
        query = query.filter(Alert.model_id == model_id)
    
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return [AlertResponse.model_validate(a) for a in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific alert by ID"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return AlertResponse.model_validate(alert)


@router.post("", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new alert"""
    new_alert = Alert(
        **alert_data.model_dump(),
        status=AlertStatus.open
    )
    
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="create",
        resource_type="alert",
        resource_id=new_alert.id,
        details={"title": new_alert.title, "type": new_alert.type}
    )
    
    return AlertResponse.model_validate(new_alert)


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Update fields
    update_data = alert_data.model_dump(exclude_unset=True)
    
    # If status is being changed to resolved, set resolved_at
    if "status" in update_data and update_data["status"] == AlertStatus.resolved:
        if alert.resolved_at is None:
            alert.resolved_at = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(alert, field, value)
    
    db.commit()
    db.refresh(alert)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="update",
        resource_type="alert",
        resource_id=alert.id,
        details={"updated_fields": list(update_data.keys())}
    )
    
    return AlertResponse.model_validate(alert)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Log audit before deleting
    log_audit(
        db=db,
        user_id=current_user.id,
        action="delete",
        resource_type="alert",
        resource_id=alert.id,
        details={"title": alert.title}
    )
    
    db.delete(alert)
    db.commit()
    
    return None


@router.post("/trigger-check", response_model=dict)
async def trigger_alert_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger alert condition checks"""
    new_alerts = []
    
    # Check for models with high risk scores without approval
    from app.models import ModelStatus, Severity
    
    high_risk_models = db.query(Model).filter(
        Model.risk_score >= 7,
        Model.status != ModelStatus.approved,
        Model.deleted_at.is_(None)
    ).all()
    
    for model in high_risk_models:
        # Check if alert already exists
        existing = db.query(Alert).filter(
            Alert.model_id == model.id,
            Alert.type == "high_risk_pending_approval",
            Alert.status != AlertStatus.resolved
        ).first()
        
        if not existing:
            alert = Alert(
                title=f"High-risk model pending approval: {model.name}",
                description=f"Model {model.name} has risk score {model.risk_score} and requires approval",
                type="high_risk_pending_approval",
                severity=Severity.high,
                model_id=model.id,
                status=AlertStatus.open
            )
            db.add(alert)
            new_alerts.append({"model": model.name, "alert_type": "high_risk_pending_approval"})
    
    # Check for models with multiple open incidents
    models_with_incidents = db.query(
        Incident.model_id,
        func.count(Incident.id).label('count')
    ).filter(
        Incident.status.in_(['open', 'investigating']),
        Incident.model_id.isnot(None)
    ).group_by(Incident.model_id).having(func.count(Incident.id) >= 3).all()
    
    for model_id, count in models_with_incidents:
        model = db.query(Model).filter(Model.id == model_id).first()
        if model:
            existing = db.query(Alert).filter(
                Alert.model_id == model.id,
                Alert.type == "multiple_open_incidents",
                Alert.status != AlertStatus.resolved
            ).first()
            
            if not existing:
                alert = Alert(
                    title=f"Multiple open incidents on {model.name}",
                    description=f"Model has {count} open incidents",
                    type="multiple_open_incidents",
                    severity=Severity.high,
                    model_id=model.id,
                    status=AlertStatus.open
                )
                db.add(alert)
                new_alerts.append({"model": model.name, "alert_type": "multiple_open_incidents"})
    
    db.commit()
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="trigger_check",
        resource_type="alert",
        details={"new_alerts_created": len(new_alerts)}
    )
    
    return {
        "message": "Alert check completed",
        "new_alerts_created": len(new_alerts),
        "alerts": new_alerts
    }
