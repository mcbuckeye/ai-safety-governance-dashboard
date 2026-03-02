from sqlalchemy.orm import Session
from app.models import (
    User, Model, ModelRiskCategory, Incident, Policy, 
    PolicyModelMapping, Alert, UserRole, ModelStatus, 
    RiskCategory, IncidentType, Severity, IncidentStatus,
    ComplianceStatus, AlertStatus
)
from app.auth import hash_password
from datetime import datetime, timedelta


def seed_database(db: Session):
    """Seed the database with initial data"""
    
    # Check if users already exist
    existing_users = db.query(User).count()
    if existing_users > 0:
        print("Database already seeded, skipping...")
        return
    
    print("Seeding database...")
    
    # Create admin user
    admin = User(
        email="steve@ipwatcher.com",
        password_hash=hash_password("5678*Stud"),
        name="Steve",
        role=UserRole.admin
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"Created admin user: {admin.email}")
    
    # Create 5 AI models with varying risk scores
    models_data = [
        {
            "name": "GPT-4 Safety Wrapper",
            "version": "1.0.0",
            "description": "Content filtering wrapper for GPT-4",
            "team": "AI Safety Team",
            "risk_score": 3.0,
            "status": ModelStatus.deployed,
            "risk_categories": [
                {"category": RiskCategory.safety, "score": 3},
                {"category": RiskCategory.bias, "score": 2},
                {"category": RiskCategory.privacy, "score": 4}
            ]
        },
        {
            "name": "Facial Recognition v2",
            "version": "2.1.0",
            "description": "Advanced facial recognition system",
            "team": "Computer Vision Team",
            "risk_score": 8.0,
            "status": ModelStatus.review,
            "risk_categories": [
                {"category": RiskCategory.bias, "score": 9},
                {"category": RiskCategory.privacy, "score": 8},
                {"category": RiskCategory.fairness, "score": 7}
            ]
        },
        {
            "name": "Sentiment Analyzer",
            "version": "1.2.0",
            "description": "Real-time sentiment analysis for customer feedback",
            "team": "NLP Team",
            "risk_score": 4.0,
            "status": ModelStatus.deployed,
            "risk_categories": [
                {"category": RiskCategory.bias, "score": 5},
                {"category": RiskCategory.fairness, "score": 4},
                {"category": RiskCategory.robustness, "score": 3}
            ]
        },
        {
            "name": "Autonomous Decision Engine",
            "version": "3.0.0",
            "description": "High-stakes automated decision making system",
            "team": "ML Research",
            "risk_score": 9.0,
            "status": ModelStatus.draft,
            "risk_categories": [
                {"category": RiskCategory.safety, "score": 9},
                {"category": RiskCategory.bias, "score": 8},
                {"category": RiskCategory.fairness, "score": 9},
                {"category": RiskCategory.robustness, "score": 8}
            ]
        },
        {
            "name": "Data Anonymizer",
            "version": "1.0.0",
            "description": "Privacy-preserving data anonymization",
            "team": "Data Privacy Team",
            "risk_score": 2.0,
            "status": ModelStatus.approved,
            "risk_categories": [
                {"category": RiskCategory.privacy, "score": 2},
                {"category": RiskCategory.robustness, "score": 3}
            ]
        }
    ]
    
    created_models = []
    for model_data in models_data:
        risk_cats = model_data.pop("risk_categories")
        model = Model(
            **model_data,
            created_by=admin.id
        )
        db.add(model)
        db.commit()
        db.refresh(model)
        
        # Add risk categories
        for cat_data in risk_cats:
            risk_cat = ModelRiskCategory(
                model_id=model.id,
                **cat_data
            )
            db.add(risk_cat)
        
        created_models.append(model)
        print(f"Created model: {model.name}")
    
    db.commit()
    
    # Create 3 policies
    policies_data = [
        {
            "name": "EU AI Act Compliance",
            "description": "Compliance requirements for EU AI Act",
            "requirements": "All high-risk AI systems must undergo conformity assessment, maintain technical documentation, and implement human oversight mechanisms.",
            "applicable_model_types": {"high_risk": True, "general_purpose": True}
        },
        {
            "name": "Bias Mitigation Standard",
            "description": "Internal standards for bias detection and mitigation",
            "requirements": "All models must be tested for bias across protected characteristics. Bias scores above 7 require mitigation plans.",
            "applicable_model_types": {"nlp": True, "computer_vision": True}
        },
        {
            "name": "Data Privacy Framework",
            "description": "Privacy requirements for data handling",
            "requirements": "All models processing personal data must implement privacy-preserving techniques and maintain audit trails.",
            "applicable_model_types": {"data_processing": True}
        }
    ]
    
    created_policies = []
    for policy_data in policies_data:
        policy = Policy(**policy_data)
        db.add(policy)
        db.commit()
        db.refresh(policy)
        created_policies.append(policy)
        print(f"Created policy: {policy.name}")
    
    # Create compliance mappings
    mappings = [
        {"policy": 0, "model": 0, "status": ComplianceStatus.compliant},
        {"policy": 0, "model": 1, "status": ComplianceStatus.pending_review},
        {"policy": 0, "model": 3, "status": ComplianceStatus.non_compliant},
        {"policy": 1, "model": 1, "status": ComplianceStatus.non_compliant},
        {"policy": 1, "model": 2, "status": ComplianceStatus.compliant},
        {"policy": 2, "model": 4, "status": ComplianceStatus.compliant},
    ]
    
    for mapping in mappings:
        pm_mapping = PolicyModelMapping(
            policy_id=created_policies[mapping["policy"]].id,
            model_id=created_models[mapping["model"]].id,
            compliance_status=mapping["status"],
            reviewed_by=admin.id if mapping["status"] != ComplianceStatus.pending_review else None,
            reviewed_at=datetime.utcnow() if mapping["status"] != ComplianceStatus.pending_review else None
        )
        db.add(pm_mapping)
    
    db.commit()
    print("Created compliance mappings")
    
    # Create 10 incidents
    incidents_data = [
        {
            "title": "Bias detected in hiring recommendations",
            "description": "Model showed preference for certain demographic groups",
            "type": IncidentType.bias_detection,
            "severity": Severity.high,
            "model_id": created_models[3].id,
            "status": IncidentStatus.investigating,
            "reported_by": admin.id,
            "assigned_to": admin.id
        },
        {
            "title": "Safety filter bypass attempt",
            "description": "User found method to bypass content safety filters",
            "type": IncidentType.safety_violation,
            "severity": Severity.critical,
            "model_id": created_models[0].id,
            "status": IncidentStatus.resolved,
            "reported_by": admin.id,
            "assigned_to": admin.id,
            "resolution_notes": "Patched filter and added additional test cases",
            "resolved_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "title": "Near-miss: incorrect medical diagnosis",
            "description": "Model nearly provided incorrect medical information before human review",
            "type": IncidentType.near_miss,
            "severity": Severity.high,
            "model_id": created_models[3].id,
            "status": IncidentStatus.open,
            "reported_by": admin.id
        },
        {
            "title": "Model drift detected in production",
            "description": "Sentiment analyzer showing degraded performance",
            "type": IncidentType.drift_alert,
            "severity": Severity.medium,
            "model_id": created_models[2].id,
            "status": IncidentStatus.investigating,
            "reported_by": admin.id,
            "assigned_to": admin.id
        },
        {
            "title": "Privacy breach - PII leakage",
            "description": "Model inadvertently included PII in training data output",
            "type": IncidentType.privacy_breach,
            "severity": Severity.critical,
            "model_id": created_models[1].id,
            "status": IncidentStatus.closed,
            "reported_by": admin.id,
            "assigned_to": admin.id,
            "resolution_notes": "Removed affected data, retrained model, implemented additional privacy controls",
            "resolved_at": datetime.utcnow() - timedelta(days=5)
        },
        {
            "title": "Facial recognition false positive spike",
            "description": "Increased false positive rate detected in recent deployments",
            "type": IncidentType.bias_detection,
            "severity": Severity.high,
            "model_id": created_models[1].id,
            "status": IncidentStatus.open,
            "reported_by": admin.id
        },
        {
            "title": "Sentiment analyzer cultural bias",
            "description": "Model showing bias against certain cultural expressions",
            "type": IncidentType.bias_detection,
            "severity": Severity.medium,
            "model_id": created_models[2].id,
            "status": IncidentStatus.resolved,
            "reported_by": admin.id,
            "assigned_to": admin.id,
            "resolution_notes": "Added diverse training data and re-evaluated",
            "resolved_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "title": "Autonomous system unexpected behavior",
            "description": "Decision engine made unexpected choices in edge cases",
            "type": IncidentType.safety_violation,
            "severity": Severity.high,
            "model_id": created_models[3].id,
            "status": IncidentStatus.investigating,
            "reported_by": admin.id,
            "assigned_to": admin.id
        },
        {
            "title": "Data anonymizer edge case failure",
            "description": "Rare case where anonymization was incomplete",
            "type": IncidentType.near_miss,
            "severity": Severity.low,
            "model_id": created_models[4].id,
            "status": IncidentStatus.resolved,
            "reported_by": admin.id,
            "assigned_to": admin.id,
            "resolution_notes": "Fixed edge case and added regression tests",
            "resolved_at": datetime.utcnow() - timedelta(hours=12)
        },
        {
            "title": "Performance degradation alert",
            "description": "GPT-4 wrapper showing increased latency",
            "type": IncidentType.drift_alert,
            "severity": Severity.info,
            "model_id": created_models[0].id,
            "status": IncidentStatus.closed,
            "reported_by": admin.id,
            "assigned_to": admin.id,
            "resolution_notes": "Identified infrastructure bottleneck, resolved",
            "resolved_at": datetime.utcnow() - timedelta(hours=6)
        }
    ]
    
    for incident_data in incidents_data:
        incident = Incident(**incident_data)
        db.add(incident)
    
    db.commit()
    print("Created 10 incidents")
    
    # Create 5 sample alerts
    alerts_data = [
        {
            "title": "High-risk model pending approval",
            "description": "Autonomous Decision Engine requires safety review",
            "type": "approval_required",
            "severity": Severity.high,
            "model_id": created_models[3].id,
            "status": AlertStatus.open,
            "assigned_to": admin.id
        },
        {
            "title": "Compliance review needed",
            "description": "Facial Recognition v2 pending EU AI Act compliance review",
            "type": "compliance",
            "severity": Severity.medium,
            "model_id": created_models[1].id,
            "status": AlertStatus.open,
            "assigned_to": admin.id
        },
        {
            "title": "Multiple open incidents on model",
            "description": "Autonomous Decision Engine has 3 open incidents",
            "type": "incident_threshold",
            "severity": Severity.high,
            "model_id": created_models[3].id,
            "status": AlertStatus.acknowledged,
            "assigned_to": admin.id
        },
        {
            "title": "Bias score threshold exceeded",
            "description": "Facial Recognition v2 bias score exceeds policy threshold",
            "type": "risk_threshold",
            "severity": Severity.critical,
            "model_id": created_models[1].id,
            "status": AlertStatus.open,
            "assigned_to": admin.id
        },
        {
            "title": "Model documentation incomplete",
            "description": "Sentiment Analyzer missing required documentation",
            "type": "documentation",
            "severity": Severity.low,
            "model_id": created_models[2].id,
            "status": AlertStatus.resolved,
            "assigned_to": admin.id,
            "resolved_at": datetime.utcnow() - timedelta(days=1)
        }
    ]
    
    for alert_data in alerts_data:
        alert = Alert(**alert_data)
        db.add(alert)
    
    db.commit()
    print("Created 5 alerts")
    
    # Create some audit log entries
    from app.models import AuditLog
    
    audit_entries = [
        {
            "user_id": admin.id,
            "action": "create",
            "resource_type": "model",
            "resource_id": created_models[0].id,
            "details": {"name": created_models[0].name}
        },
        {
            "user_id": admin.id,
            "action": "update",
            "resource_type": "incident",
            "resource_id": 1,
            "details": {"status": "resolved"}
        },
        {
            "user_id": admin.id,
            "action": "create",
            "resource_type": "policy",
            "resource_id": created_policies[0].id,
            "details": {"name": created_policies[0].name}
        },
        {
            "user_id": admin.id,
            "action": "review",
            "resource_type": "compliance",
            "resource_id": 1,
            "details": {"status": "compliant"}
        }
    ]
    
    for entry_data in audit_entries:
        entry = AuditLog(**entry_data)
        db.add(entry)
    
    db.commit()
    print("Created audit log entries")
    
    print("Database seeding complete!")
