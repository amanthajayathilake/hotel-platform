from typing import List
from datetime import date
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models.room_type import RoomType
from app.models.hotel import Hotel
from app.models.rate_adjustment import RateAdjustment
from app.models.user import User
from app.schemas import RoomTypeCreate, RoomTypeUpdate, RoomTypeResponse, MessageResponse
from app.utils.auth import get_current_user
from app.utils.cloudinary import upload_multiple_images, delete_multiple_images

router = APIRouter(prefix="/room-types", tags=["Room Types"])


def calculate_effective_rate(room_type: RoomType, db: Session, target_date: date = None) -> Decimal:
    """
    Calculate the effective rate for a room type based on adjustments.
    Formula: effective_rate = base_rate + adjustment_amount
    
    Uses the latest adjustment where effective_date <= target_date
    """
    if target_date is None:
        target_date = date.today()
    
    # Get the most recent adjustment that's effective on or before the target date
    latest_adjustment = db.query(RateAdjustment).filter(
        and_(
            RateAdjustment.room_type_id == room_type.id,
            RateAdjustment.effective_date <= target_date
        )
    ).order_by(RateAdjustment.effective_date.desc()).first()
    
    # Calculate effective rate
    if latest_adjustment:
        return room_type.base_rate + latest_adjustment.adjustment_amount
    
    return room_type.base_rate


@router.get("", response_model=List[RoomTypeResponse])
def get_room_types(
    hotel_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all room types with optional hotel filtering.
    Includes calculated effective rates.
    """
    query = db.query(RoomType)
    
    if hotel_id:
        query = query.filter(RoomType.hotel_id == hotel_id)
    
    room_types = query.offset(skip).limit(limit).all()
    
    # Add effective rates to response
    response = []
    for room_type in room_types:
        room_dict = RoomTypeResponse.from_orm(room_type).dict()
        room_dict['effective_rate'] = calculate_effective_rate(room_type, db)
        response.append(RoomTypeResponse(**room_dict))
    
    return response


@router.get("/{room_type_id}", response_model=RoomTypeResponse)
def get_room_type(
    room_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific room type by ID with effective rate.
    """
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room type with id {room_type_id} not found"
        )
    
    # Add effective rate
    room_dict = RoomTypeResponse.from_orm(room_type).dict()
    room_dict['effective_rate'] = calculate_effective_rate(room_type, db)
    
    return RoomTypeResponse(**room_dict)


@router.post("", response_model=RoomTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_room_type(
    hotel_id: int = Form(...),
    name: str = Form(...),
    description: str = Form(None),
    base_rate: float = Form(...),
    max_occupancy: int = Form(2),
    size_sqm: int = Form(None),
    images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new room type with optional image uploads.
    Maximum 3 images allowed per room type.
    """
    # Verify hotel exists
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotel with id {hotel_id} not found"
        )
    
    # Validate base rate
    if base_rate <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Base rate must be greater than 0"
        )
    
    # Upload images to Cloudinary if provided
    image_urls = []
    if images:
        if len(images) > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 3 images allowed"
            )
        image_urls = await upload_multiple_images(images, folder="room-types")
    
    # Create room type
    room_type = RoomType(
        hotel_id=hotel_id,
        name=name,
        description=description,
        base_rate=Decimal(str(base_rate)),
        max_occupancy=max_occupancy,
        size_sqm=size_sqm,
        images=image_urls
    )
    
    db.add(room_type)
    db.commit()
    db.refresh(room_type)
    
    # Add effective rate to response
    room_dict = RoomTypeResponse.from_orm(room_type).dict()
    room_dict['effective_rate'] = calculate_effective_rate(room_type, db)
    
    return RoomTypeResponse(**room_dict)


@router.put("/{room_type_id}", response_model=RoomTypeResponse)
async def update_room_type(
    room_type_id: int,
    name: str = Form(None),
    description: str = Form(None),
    base_rate: float = Form(None),
    max_occupancy: int = Form(None),
    size_sqm: int = Form(None),
    is_active: bool = Form(None),
    images: List[UploadFile] = File(default=[]),
    replace_images: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing room type.
    
    If replace_images is True, old images will be deleted and replaced.
    If False, new images will be appended (up to max 3 total).
    """
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room type with id {room_type_id} not found"
        )
    
    # Handle image uploads
    if images:
        new_image_urls = await upload_multiple_images(images, folder="room-types")
        
        if replace_images:
            # Delete old images from Cloudinary
            if room_type.images:
                delete_multiple_images(room_type.images)
            room_type.images = new_image_urls
        else:
            # Append new images (ensure max 3)
            current_images = room_type.images or []
            combined = current_images + new_image_urls
            
            if len(combined) > 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Total images would exceed maximum of 3"
                )
            
            room_type.images = combined
    
    # Update other fields if provided
    if name is not None:
        room_type.name = name
    if description is not None:
        room_type.description = description
    if base_rate is not None:
        if base_rate <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Base rate must be greater than 0"
            )
        room_type.base_rate = Decimal(str(base_rate))
    if max_occupancy is not None:
        room_type.max_occupancy = max_occupancy
    if size_sqm is not None:
        room_type.size_sqm = size_sqm
    if is_active is not None:
        room_type.is_active = is_active
    
    db.commit()
    db.refresh(room_type)
    
    # Add effective rate to response
    room_dict = RoomTypeResponse.from_orm(room_type).dict()
    room_dict['effective_rate'] = calculate_effective_rate(room_type, db)
    
    return RoomTypeResponse(**room_dict)


@router.delete("/{room_type_id}", response_model=MessageResponse)
def delete_room_type(
    room_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a room type and all associated rate adjustments.
    Also deletes images from Cloudinary.
    """
    room_type = db.query(RoomType).filter(RoomType.id == room_type_id).first()
    
    if not room_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room type with id {room_type_id} not found"
        )
    
    # Delete images from Cloudinary
    if room_type.images:
        delete_multiple_images(room_type.images)
    
    db.delete(room_type)
    db.commit()
    
    return {
        "message": "Room type deleted successfully",
        "detail": f"Deleted room type: {room_type.name}"
    }
