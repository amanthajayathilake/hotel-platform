from typing import List
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.rate_adjustment import RateAdjustment
from app.models.room_type import RoomType
from app.models.user import User
from app.schemas import RateAdjustmentCreate, RateAdjustmentResponse, MessageResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/rate-adjustments", tags=["Rate Adjustments"])


@router.get("", response_model=List[RateAdjustmentResponse])
def get_rate_adjustments(
    room_type_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all rate adjustments with optional room type filtering.
    Returns history sorted by effective date (newest first).
    """
    query = db.query(RateAdjustment)
    
    if room_type_id:
        query = query.filter(RateAdjustment.room_type_id == room_type_id)
    
    # Order by effective date descending to show most recent first
    adjustments = query.order_by(
        RateAdjustment.effective_date.desc()
    ).offset(skip).limit(limit).all()
    
    return adjustments


@router.get("/{adjustment_id}", response_model=RateAdjustmentResponse)
def get_rate_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific rate adjustment by ID.
    """
    adjustment = db.query(RateAdjustment).filter(
        RateAdjustment.id == adjustment_id
    ).first()
    
    if not adjustment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rate adjustment with id {adjustment_id} not found"
        )
    
    return adjustment


@router.post("", response_model=RateAdjustmentResponse, status_code=status.HTTP_201_CREATED)
def create_rate_adjustment(
    adjustment_data: RateAdjustmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new rate adjustment for a room type.
    
    The adjustment amount will be added to the base rate.
    This creates a historical record with reason and effective date.
    
    Example: If base rate is $100 and adjustment is +$20,
    the effective rate becomes $120 from the effective date onwards.
    """
    # Verify room type exists
    room_type = db.query(RoomType).filter(
        RoomType.id == adjustment_data.room_type_id
    ).first()
    
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room type with id {adjustment_data.room_type_id} not found"
        )
    
    # Create rate adjustment
    adjustment = RateAdjustment(
        room_type_id=adjustment_data.room_type_id,
        adjustment_amount=adjustment_data.adjustment_amount,
        effective_date=adjustment_data.effective_date,
        reason=adjustment_data.reason,
        created_by=adjustment_data.created_by or current_user.username
    )
    
    db.add(adjustment)
    db.commit()
    db.refresh(adjustment)
    
    return adjustment


@router.delete("/{adjustment_id}", response_model=MessageResponse)
def delete_rate_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a rate adjustment from history.
    
    Note: This will affect the effective rate calculation if it was
    the most recent adjustment for a room type.
    """
    adjustment = db.query(RateAdjustment).filter(
        RateAdjustment.id == adjustment_id
    ).first()
    
    if not adjustment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rate adjustment with id {adjustment_id} not found"
        )
    
    db.delete(adjustment)
    db.commit()
    
    return {
        "message": "Rate adjustment deleted successfully",
        "detail": f"Deleted adjustment with effective date: {adjustment.effective_date}"
    }


@router.get("/room-type/{room_type_id}/history", response_model=List[RateAdjustmentResponse])
def get_room_type_rate_history(
    room_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete rate adjustment history for a specific room type.
    Sorted by effective date (newest first).
    """
    # Verify room type exists
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room type with id {room_type_id} not found"
        )
    
    # Get all adjustments for this room type
    adjustments = db.query(RateAdjustment).filter(
        RateAdjustment.room_type_id == room_type_id
    ).order_by(RateAdjustment.effective_date.desc()).all()
    
    return adjustments
