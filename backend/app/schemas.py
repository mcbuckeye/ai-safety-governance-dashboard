from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import (
    UserRole, ModelStatus, RiskCategory, IncidentType, 
    Severity, IncidentStatus, ComplianceStatus, AlertStatus
)


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Model Schemas
class ModelRiskCategoryBase(BaseModel):
    category: RiskCategory
    score: int


class ModelRiskCategoryCreate(ModelRiskCategoryBase):
    pass


class ModelRiskCategoryResponse(ModelRiskCategoryBase):
    id: int
    model_id: int
    
    class Config:
        from_attributes = True


class ModelBase(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    team: Optional[str] = None
    risk_score: float
    status: ModelStatus


class ModelCreate(ModelBase):
    risk_categories: Optional[List[ModelRiskCategoryCreate]] = []


class ModelUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    team: Optional[str] = None
    risk_score: Optional[float] = None
    status: Optional[ModelStatus] = None


class ModelResponse(ModelBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    risk_level: str
    risk_categories: List[ModelRiskCategoryResponse] = []
    
    class Config:
        from_attributes = True


# Incident Schemas
class IncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: IncidentType
    severity: Severity
    model_id: Optional[int] = None
    status: IncidentStatus
    assigned_to: Optional[int] = None
    resolution_notes: Optional[str] = None


class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: IncidentType
    severity: Severity
    model_id: Optional[int] = None
    assigned_to: Optional[int] = None


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[IncidentType] = None
    severity: Optional[Severity] = None
    model_id: Optional[int] = None
    status: Optional[IncidentStatus] = None
    assigned_to: Optional[int] = None
    resolution_notes: Optional[str] = None


class IncidentResponse(IncidentBase):
    id: int
    reported_by: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Policy Schemas
class PolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    requirements: str
    applicable_model_types: Optional[Dict[str, Any]] = None


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    applicable_model_types: Optional[Dict[str, Any]] = None


class PolicyResponse(PolicyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Policy Model Mapping Schemas
class PolicyModelMappingBase(BaseModel):
    policy_id: int
    model_id: int
    compliance_status: ComplianceStatus
    notes: Optional[str] = None


class PolicyModelMappingCreate(BaseModel):
    policy_id: int
    model_id: int
    notes: Optional[str] = None


class PolicyModelMappingUpdate(BaseModel):
    compliance_status: Optional[ComplianceStatus] = None
    notes: Optional[str] = None


class PolicyModelMappingResponse(PolicyModelMappingBase):
    id: int
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Alert Schemas
class AlertBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: str
    severity: Severity
    model_id: Optional[int] = None
    status: AlertStatus
    assigned_to: Optional[int] = None


class AlertCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: str
    severity: Severity
    model_id: Optional[int] = None
    assigned_to: Optional[int] = None


class AlertUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    severity: Optional[Severity] = None
    model_id: Optional[int] = None
    status: Optional[AlertStatus] = None
    assigned_to: Optional[int] = None


class AlertResponse(AlertBase):
    id: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Dashboard Schemas
class RiskDistribution(BaseModel):
    low: int
    medium: int
    high: int
    critical: int


class DashboardSummary(BaseModel):
    total_models: int
    risk_distribution: RiskDistribution
    total_incidents: int
    open_incidents: int
    compliance_score: float
    total_policies: int
    open_alerts: int
    recent_incidents: List[IncidentResponse]
    recent_audit: List[AuditLogResponse]
