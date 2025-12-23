"""
Audit log API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional

from app.core.database import get_db
from app.models.database import User, AuditLog
from app.models.schemas import AuditLogResponse, AuditLogListResponse
from app.api.dependencies import get_current_user, require_admin


router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.get("/logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = None,
    action_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get audit logs (Admin only).
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **user_id**: Filter by user ID
    - **action_type**: Filter by action type (enrollment, authentication, approval)
    
    Returns paginated list of audit logs.
    """
    # Build query
    query = select(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    
    if action_type:
        query = query.where(AuditLog.action_type == action_type)
    
    # Order by timestamp descending
    query = query.order_by(desc(AuditLog.timestamp))
    
    # Get total count
    count_query = select(func.count()).select_from(AuditLog)
    if user_id:
        count_query = count_query.where(AuditLog.user_id == user_id)
    if action_type:
        count_query = count_query.where(AuditLog.action_type == action_type)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return AuditLogListResponse(
        total=total,
        logs=[AuditLogResponse.model_validate(log) for log in logs]
    )


@router.get("/logs/user/{user_id}", response_model=AuditLogListResponse)
async def get_user_audit_logs(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs for a specific user.
    
    Users can only see their own logs unless they are admin.
    """
    # Check permissions
    if current_user.id != user_id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own audit logs"
        )
    
    # Build query
    query = select(AuditLog).where(AuditLog.user_id == user_id)
    query = query.order_by(desc(AuditLog.timestamp))
    
    # Get total count
    count_query = select(func.count()).select_from(AuditLog).where(AuditLog.user_id == user_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return AuditLogListResponse(
        total=total,
        logs=[AuditLogResponse.model_validate(log) for log in logs]
    )
