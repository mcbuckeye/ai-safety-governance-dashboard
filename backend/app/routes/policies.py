from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models import Policy, PolicyModelMapping, User, Model
from app.schemas import (
    PolicyCreate, PolicyUpdate, PolicyResponse,
    PolicyModelMappingCreate, PolicyModelMappingUpdate, PolicyModelMappingResponse
)
from app.auth import get_current_user, log_audit

router = APIRouter(prefix="/api/policies", tags=["policies"])


@router.get("", response_model=List[PolicyResponse])
async def list_policies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all policies"""
    policies = db.query(Policy).offset(skip).limit(limit).all()
    return [PolicyResponse.model_validate(p) for p in policies]


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific policy by ID"""
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    return PolicyResponse.model_validate(policy)


@router.post("", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy_data: PolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new policy"""
    new_policy = Policy(**policy_data.model_dump())
    
    db.add(new_policy)
    db.commit()
    db.refresh(new_policy)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="create",
        resource_type="policy",
        resource_id=new_policy.id,
        details={"name": new_policy.name}
    )
    
    return PolicyResponse.model_validate(new_policy)


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: int,
    policy_data: PolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a policy"""
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Update fields
    update_data = policy_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(policy, field, value)
    
    db.commit()
    db.refresh(policy)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="update",
        resource_type="policy",
        resource_id=policy.id,
        details={"updated_fields": list(update_data.keys())}
    )
    
    return PolicyResponse.model_validate(policy)


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a policy"""
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Log audit before deleting
    log_audit(
        db=db,
        user_id=current_user.id,
        action="delete",
        resource_type="policy",
        resource_id=policy.id,
        details={"name": policy.name}
    )
    
    db.delete(policy)
    db.commit()
    
    return None


@router.post("/{policy_id}/models", response_model=PolicyModelMappingResponse, status_code=status.HTTP_201_CREATED)
async def map_policy_to_model(
    policy_id: int,
    mapping_data: PolicyModelMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Map a policy to a model for compliance tracking"""
    # Verify policy exists
    policy = db.query(Policy).filter(Policy.id == policy_id).first()
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    # Verify model exists
    model = db.query(Model).filter(Model.id == mapping_data.model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Check if mapping already exists
    existing_mapping = db.query(PolicyModelMapping).filter(
        PolicyModelMapping.policy_id == policy_id,
        PolicyModelMapping.model_id == mapping_data.model_id
    ).first()
    
    if existing_mapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Policy already mapped to this model"
        )
    
    # Create mapping
    new_mapping = PolicyModelMapping(
        policy_id=policy_id,
        model_id=mapping_data.model_id,
        notes=mapping_data.notes
    )
    
    db.add(new_mapping)
    db.commit()
    db.refresh(new_mapping)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="create",
        resource_type="policy_mapping",
        resource_id=new_mapping.id,
        details={"policy_id": policy_id, "model_id": mapping_data.model_id}
    )
    
    return PolicyModelMappingResponse.model_validate(new_mapping)


@router.put("/mappings/{mapping_id}", response_model=PolicyModelMappingResponse)
async def update_policy_mapping(
    mapping_id: int,
    mapping_data: PolicyModelMappingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a policy-model mapping"""
    mapping = db.query(PolicyModelMapping).filter(PolicyModelMapping.id == mapping_id).first()
    
    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mapping not found"
        )
    
    # Update fields
    update_data = mapping_data.model_dump(exclude_unset=True)
    
    # If compliance status is being updated, record reviewer and timestamp
    if "compliance_status" in update_data:
        mapping.reviewed_by = current_user.id
        mapping.reviewed_at = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(mapping, field, value)
    
    db.commit()
    db.refresh(mapping)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="update",
        resource_type="policy_mapping",
        resource_id=mapping.id,
        details={"updated_fields": list(update_data.keys())}
    )
    
    return PolicyModelMappingResponse.model_validate(mapping)


@router.get("/compliance/matrix", response_model=dict)
async def get_compliance_matrix(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get compliance matrix showing all policy-model mappings"""
    # Get all policies
    policies = db.query(Policy).all()
    
    # Get all non-deleted models
    models = db.query(Model).filter(Model.deleted_at.is_(None)).all()
    
    # Get all mappings
    mappings = db.query(PolicyModelMapping).all()
    
    # Build matrix
    matrix = {}
    for policy in policies:
        policy_mappings = [m for m in mappings if m.policy_id == policy.id]
        matrix[policy.name] = {
            "policy_id": policy.id,
            "models": {}
        }
        
        for mapping in policy_mappings:
            model = next((m for m in models if m.id == mapping.model_id), None)
            if model:
                matrix[policy.name]["models"][model.name] = {
                    "model_id": model.id,
                    "compliance_status": str(mapping.compliance_status),
                    "reviewed_by": mapping.reviewed_by,
                    "reviewed_at": mapping.reviewed_at,
                    "notes": mapping.notes
                }
    
    return {
        "matrix": matrix,
        "summary": {
            "total_policies": len(policies),
            "total_models": len(models),
            "total_mappings": len(mappings)
        }
    }
