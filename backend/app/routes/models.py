from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Model, User, ModelRiskCategory, ModelStatus
from app.schemas import ModelCreate, ModelUpdate, ModelResponse, ModelRiskCategoryCreate
from app.auth import get_current_user, log_audit

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("", response_model=List[ModelResponse])
async def list_models(
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all models"""
    query = db.query(Model)
    
    if not include_deleted:
        query = query.filter(Model.deleted_at.is_(None))
    
    models = query.offset(skip).limit(limit).all()
    return [ModelResponse.model_validate(m) for m in models]


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific model by ID"""
    model = db.query(Model).filter(Model.id == model_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return ModelResponse.model_validate(model)


@router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    model_data: ModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new model"""
    # Extract risk categories
    risk_categories_data = model_data.risk_categories
    model_dict = model_data.model_dump(exclude={"risk_categories"})
    
    # Create model
    new_model = Model(
        **model_dict,
        created_by=current_user.id
    )
    
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    
    # Add risk categories
    if risk_categories_data:
        for cat_data in risk_categories_data:
            risk_cat = ModelRiskCategory(
                model_id=new_model.id,
                category=cat_data.category,
                score=cat_data.score
            )
            db.add(risk_cat)
        db.commit()
        db.refresh(new_model)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="create",
        resource_type="model",
        resource_id=new_model.id,
        details={"name": new_model.name, "version": new_model.version}
    )
    
    return ModelResponse.model_validate(new_model)


@router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: int,
    model_data: ModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a model"""
    model = db.query(Model).filter(Model.id == model_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Update fields
    update_data = model_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model, field, value)
    
    db.commit()
    db.refresh(model)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="update",
        resource_type="model",
        resource_id=model.id,
        details={"updated_fields": list(update_data.keys())}
    )
    
    return ModelResponse.model_validate(model)


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    hard_delete: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete or hard delete a model"""
    model = db.query(Model).filter(Model.id == model_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    if hard_delete:
        db.delete(model)
        action = "hard_delete"
    else:
        from datetime import datetime
        model.deleted_at = datetime.utcnow()
        action = "soft_delete"
    
    db.commit()
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action=action,
        resource_type="model",
        resource_id=model.id,
        details={"name": model.name}
    )
    
    return None


@router.post("/{model_id}/approve", response_model=ModelResponse)
async def approve_model(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a model (change status to approved)"""
    model = db.query(Model).filter(Model.id == model_id).first()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    old_status = model.status
    model.status = ModelStatus.approved
    
    db.commit()
    db.refresh(model)
    
    # Log audit
    log_audit(
        db=db,
        user_id=current_user.id,
        action="approve",
        resource_type="model",
        resource_id=model.id,
        details={"old_status": old_status, "new_status": ModelStatus.approved}
    )
    
    return ModelResponse.model_validate(model)


@router.get("/{model_id}/history", response_model=dict)
async def get_model_history(
    model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get audit history for a model"""
    from app.models import AuditLog
    
    # Verify model exists
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    # Get audit logs for this model
    logs = db.query(AuditLog).filter(
        AuditLog.resource_type == "model",
        AuditLog.resource_id == model_id
    ).order_by(AuditLog.created_at.desc()).all()
    
    return {
        "model_id": model_id,
        "model_name": model.name,
        "history": [
            {
                "action": log.action,
                "user_id": log.user_id,
                "details": log.details,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }
