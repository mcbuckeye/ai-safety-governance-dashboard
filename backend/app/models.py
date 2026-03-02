from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    safety_officer = "safety_officer"
    engineer = "engineer"
    viewer = "viewer"


class ModelStatus(str, enum.Enum):
    draft = "draft"
    review = "review"
    approved = "approved"
    deployed = "deployed"
    retired = "retired"


class RiskCategory(str, enum.Enum):
    bias = "bias"
    safety = "safety"
    privacy = "privacy"
    robustness = "robustness"
    fairness = "fairness"


class IncidentType(str, enum.Enum):
    bias_detection = "bias_detection"
    safety_violation = "safety_violation"
    near_miss = "near_miss"
    drift_alert = "drift_alert"
    privacy_breach = "privacy_breach"


class Severity(str, enum.Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IncidentStatus(str, enum.Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"
    closed = "closed"


class ComplianceStatus(str, enum.Enum):
    compliant = "compliant"
    non_compliant = "non_compliant"
    pending_review = "pending_review"
    exempt = "exempt"


class AlertStatus(str, enum.Enum):
    open = "open"
    acknowledged = "acknowledged"
    resolved = "resolved"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.viewer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    created_models = relationship("Model", foreign_keys="Model.created_by", back_populates="creator")
    reported_incidents = relationship("Incident", foreign_keys="Incident.reported_by", back_populates="reporter")
    assigned_incidents = relationship("Incident", foreign_keys="Incident.assigned_to", back_populates="assignee")
    assigned_alerts = relationship("Alert", foreign_keys="Alert.assigned_to", back_populates="assignee")
    audit_logs = relationship("AuditLog", back_populates="user")


class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    description = Column(Text)
    team = Column(String)
    risk_score = Column(Float, nullable=False)
    status = Column(Enum(ModelStatus), nullable=False, default=ModelStatus.draft)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_models")
    risk_categories = relationship("ModelRiskCategory", back_populates="model", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="model")
    policy_mappings = relationship("PolicyModelMapping", back_populates="model")
    alerts = relationship("Alert", back_populates="model")
    
    @property
    def risk_level(self):
        """Compute risk level from risk score"""
        if self.risk_score <= 3:
            return "Low"
        elif self.risk_score <= 6:
            return "Medium"
        elif self.risk_score <= 8:
            return "High"
        else:
            return "Critical"


class ModelRiskCategory(Base):
    __tablename__ = "model_risk_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    category = Column(Enum(RiskCategory), nullable=False)
    score = Column(Integer, nullable=False)  # 1-10
    
    # Relationships
    model = relationship("Model", back_populates="risk_categories")


class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    type = Column(Enum(IncidentType), nullable=False)
    severity = Column(Enum(Severity), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    status = Column(Enum(IncidentStatus), nullable=False, default=IncidentStatus.open)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    model = relationship("Model", back_populates="incidents")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_incidents")
    reporter = relationship("User", foreign_keys=[reported_by], back_populates="reported_incidents")


class Policy(Base):
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    requirements = Column(Text, nullable=False)
    applicable_model_types = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    model_mappings = relationship("PolicyModelMapping", back_populates="policy")


class PolicyModelMapping(Base):
    __tablename__ = "policy_model_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    compliance_status = Column(Enum(ComplianceStatus), nullable=False, default=ComplianceStatus.pending_review)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    policy = relationship("Policy", back_populates="model_mappings")
    model = relationship("Model", back_populates="policy_mappings")
    reviewer = relationship("User")


class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    type = Column(String, nullable=False)
    severity = Column(Enum(Severity), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    status = Column(Enum(AlertStatus), nullable=False, default=AlertStatus.open)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    model = relationship("Model", back_populates="alerts")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_alerts")
