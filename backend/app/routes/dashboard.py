from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import (
    Model, Incident, Policy, PolicyModelMapping, 
    AuditLog, Alert, User, IncidentStatus, AlertStatus, ComplianceStatus
)
from app.schemas import DashboardSummary, RiskDistribution, IncidentResponse, AuditLogResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard summary with all key metrics"""
    
    # Total models (excluding soft-deleted)
    total_models = db.query(func.count(Model.id)).filter(
        Model.deleted_at.is_(None)
    ).scalar()
    
    # Risk distribution
    risk_levels = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0
    }
    
    models = db.query(Model).filter(Model.deleted_at.is_(None)).all()
    for model in models:
        level = model.risk_level.lower()
        if level in risk_levels:
            risk_levels[level] += 1
    
    # Incidents
    total_incidents = db.query(func.count(Incident.id)).scalar()
    
    open_incidents = db.query(func.count(Incident.id)).filter(
        Incident.status.in_([IncidentStatus.open, IncidentStatus.investigating])
    ).scalar()
    
    # Compliance score
    total_mappings = db.query(func.count(PolicyModelMapping.id)).scalar()
    
    if total_mappings > 0:
        compliant_mappings = db.query(func.count(PolicyModelMapping.id)).filter(
            PolicyModelMapping.compliance_status == ComplianceStatus.compliant
        ).scalar()
        compliance_score = (compliant_mappings / total_mappings) * 100
    else:
        compliance_score = 0.0
    
    # Policies
    total_policies = db.query(func.count(Policy.id)).scalar()
    
    # Alerts
    open_alerts = db.query(func.count(Alert.id)).filter(
        Alert.status.in_([AlertStatus.open, AlertStatus.acknowledged])
    ).scalar()
    
    # Recent incidents (last 5)
    recent_incidents_data = db.query(Incident).order_by(
        Incident.created_at.desc()
    ).limit(5).all()
    
    recent_incidents = [
        IncidentResponse.model_validate(incident) 
        for incident in recent_incidents_data
    ]
    
    # Recent audit logs (last 10)
    recent_audit_data = db.query(AuditLog).order_by(
        AuditLog.created_at.desc()
    ).limit(10).all()
    
    recent_audit = [
        AuditLogResponse.model_validate(log) 
        for log in recent_audit_data
    ]
    
    return DashboardSummary(
        total_models=total_models,
        risk_distribution=RiskDistribution(**risk_levels),
        total_incidents=total_incidents,
        open_incidents=open_incidents,
        compliance_score=round(compliance_score, 2),
        total_policies=total_policies,
        open_alerts=open_alerts,
        recent_incidents=recent_incidents,
        recent_audit=recent_audit
    )
