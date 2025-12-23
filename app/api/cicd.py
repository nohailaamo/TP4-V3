"""
CI/CD action approval API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.models.database import User, CICDAction, ActionStatus, AuditLog, BiometricType
from app.models.schemas import (
    CICDActionRequest,
    CICDActionResponse,
    ActionApprovalResponse,
    BiometricTypeEnum
)
from app.services.biometric import biometric_service
from app.api.dependencies import get_current_active_user, validate_biometric_file


router = APIRouter(prefix="/api/cicd", tags=["CI/CD Actions"])


@router.post("/request-action", response_model=CICDActionResponse)
async def request_cicd_action(
    action_data: CICDActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Request a CI/CD action that requires biometric approval.
    
    Creates a pending action that must be approved via biometric authentication.
    
    - **action_type**: Type of action (deploy, rollback, pipeline_modify)
    - **description**: Description of the action
    - **pipeline_id**: Optional pipeline ID
    - **environment**: Optional environment (production, staging, etc.)
    
    Returns action ID and expiration time.
    """
    # Generate unique action ID
    action_id = str(uuid.uuid4())
    
    # Create action with 15 minute expiration
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    cicd_action = CICDAction(
        action_id=action_id,
        action_type=action_data.action_type,
        description=action_data.description,
        requester_id=current_user.id,
        status=ActionStatus.PENDING,
        expires_at=expires_at,
        pipeline_id=action_data.pipeline_id,
        environment=action_data.environment
    )
    
    db.add(cicd_action)
    
    # Log action request
    audit_log = AuditLog(
        user_id=current_user.id,
        action=f"CI/CD action requested: {action_data.action_type}",
        action_type="approval",
        status=ActionStatus.PENDING,
        pipeline_id=action_data.pipeline_id,
        pipeline_action=action_data.action_type,
        details=action_data.description,
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    
    await db.commit()
    
    return CICDActionResponse(
        action_id=action_id,
        status=ActionStatus.PENDING,
        message="Action created. Please approve using biometric authentication.",
        expires_at=expires_at
    )


@router.post("/approve-action", response_model=ActionApprovalResponse)
async def approve_cicd_action(
    action_id: str = Form(...),
    biometric_type: BiometricTypeEnum = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Approve a CI/CD action using biometric authentication.
    
    This is the critical endpoint that secures CI/CD pipeline actions.
    
    - **action_id**: Action ID to approve
    - **biometric_type**: Type of biometric to use (face, voice)
    - **file**: Biometric data file
    
    Returns approval status and similarity score.
    """
    # Get action
    result = await db.execute(
        select(CICDAction).where(CICDAction.action_id == action_id)
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    
    # Check if action is still pending
    if action.status != ActionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Action is already {action.status.value}"
        )
    
    # Check if action has expired
    if datetime.utcnow() > action.expires_at:
        action.status = ActionStatus.DENIED
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action has expired"
        )
    
    # Validate biometric file
    biometric_data = await validate_biometric_file(file)
    
    # Convert enum to BiometricType
    bio_type = BiometricType[biometric_type.value.upper()]
    
    # Authenticate using biometric
    auth_result = await biometric_service.authenticate_biometric(
        db=db,
        user_id=current_user.id,
        biometric_type=bio_type,
        biometric_data=biometric_data
    )
    
    if not auth_result["success"]:
        # Update action status
        action.status = ActionStatus.DENIED
        
        # Log failed approval
        audit_log = AuditLog(
            user_id=current_user.id,
            action=f"CI/CD action approval failed: {action.action_type}",
            action_type="approval",
            status=ActionStatus.DENIED,
            biometric_type=bio_type,
            pipeline_id=action.pipeline_id,
            pipeline_action=action.action_type,
            details=auth_result["message"],
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        await db.commit()
        
        return ActionApprovalResponse(
            success=False,
            action_id=action_id,
            status=ActionStatus.DENIED,
            approved=False,
            message="Biometric authentication failed",
            similarity_score=auth_result.get("similarity_score")
        )
    
    # Check if biometric authentication succeeded
    if not auth_result["authenticated"]:
        action.status = ActionStatus.DENIED
        
        audit_log = AuditLog(
            user_id=current_user.id,
            action=f"CI/CD action denied: {action.action_type}",
            action_type="approval",
            status=ActionStatus.DENIED,
            biometric_type=bio_type,
            similarity_score=auth_result.get("similarity_score"),
            pipeline_id=action.pipeline_id,
            pipeline_action=action.action_type,
            details="Biometric verification failed",
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        await db.commit()
        
        return ActionApprovalResponse(
            success=False,
            action_id=action_id,
            status=ActionStatus.DENIED,
            approved=False,
            message="Biometric verification failed. Action denied.",
            similarity_score=auth_result.get("similarity_score")
        )
    
    # Approve action
    action.status = ActionStatus.APPROVED
    action.approver_id = current_user.id
    action.approval_method = biometric_type.value
    action.approved_at = datetime.utcnow()
    
    # Log successful approval
    audit_log = AuditLog(
        user_id=current_user.id,
        action=f"CI/CD action approved: {action.action_type}",
        action_type="approval",
        status=ActionStatus.APPROVED,
        biometric_type=bio_type,
        similarity_score=auth_result.get("similarity_score"),
        pipeline_id=action.pipeline_id,
        pipeline_action=action.action_type,
        details=f"Action approved via {biometric_type.value}",
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    
    await db.commit()
    
    return ActionApprovalResponse(
        success=True,
        action_id=action_id,
        status=ActionStatus.APPROVED,
        approved=True,
        message="Action approved successfully. CI/CD pipeline can proceed.",
        similarity_score=auth_result.get("similarity_score")
    )


@router.get("/action-status/{action_id}", response_model=CICDActionResponse)
async def get_action_status(
    action_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the status of a CI/CD action.
    
    Returns current status (pending, approved, or denied).
    """
    result = await db.execute(
        select(CICDAction).where(CICDAction.action_id == action_id)
    )
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Action not found"
        )
    
    return CICDActionResponse(
        action_id=action.action_id,
        status=action.status,
        message=f"Action is {action.status.value}",
        expires_at=action.expires_at
    )
