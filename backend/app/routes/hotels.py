from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models.hotel import Hotel
from app.models.user import User
from app.schemas import HotelCreate, HotelUpdate, HotelResponse, MessageResponse
from app.utils.auth import get_current_user
from app.utils.cloudinary import upload_multiple_images, delete_multiple_images

router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get("", response_model=List[HotelResponse])
def get_hotels(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    city: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all hotels with optional filtering.
    Supports pagination and filtering by status and city.
    """
    query = db.query(Hotel)
    
    # Apply filters if provided
    if status:
        query = query.filter(Hotel.status == status)
    
    if city:
        query = query.filter(Hotel.city.ilike(f"%{city}%"))
    
    hotels = query.offset(skip).limit(limit).all()
    return hotels


@router.get("/{hotel_id}", response_model=HotelResponse)
def get_hotel(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific hotel by ID.
    """
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotel with id {hotel_id} not found"
        )
    
    return hotel


@router.post("", response_model=HotelResponse, status_code=status.HTTP_201_CREATED)
async def create_hotel(
    name: str = Form(...),
    description: str = Form(None),
    address: str = Form(None),
    city: str = Form(None),
    country: str = Form(None),
    phone: str = Form(None),
    email: str = Form(None),
    images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new hotel with optional image uploads.
    Maximum 3 images allowed per hotel.
    """
    # Upload images to Cloudinary if provided
    image_urls = []
    if images:
        if len(images) > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 3 images allowed"
            )
        image_urls = await upload_multiple_images(images, folder="hotels")
    
    # Create hotel instance
    hotel = Hotel(
        name=name,
        description=description,
        address=address,
        city=city,
        country=country,
        phone=phone,
        email=email,
        images=image_urls
    )
    
    db.add(hotel)
    db.commit()
    db.refresh(hotel)
    
    return hotel


@router.put("/{hotel_id}", response_model=HotelResponse)
async def update_hotel(
    hotel_id: int,
    name: str = Form(None),
    description: str = Form(None),
    address: str = Form(None),
    city: str = Form(None),
    country: str = Form(None),
    phone: str = Form(None),
    email: str = Form(None),
    status_field: str = Form(None),
    is_active: bool = Form(None),
    images: List[UploadFile] = File(default=[]),
    replace_images: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing hotel.
    
    If replace_images is True, old images will be deleted and replaced.
    If False, new images will be appended (up to max 3 total).
    """
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotel with id {hotel_id} not found"
        )
    
    # Handle image uploads
    if images:
        new_image_urls = await upload_multiple_images(images, folder="hotels")
        
        if replace_images:
            # Delete old images from Cloudinary
            if hotel.images:
                delete_multiple_images(hotel.images)
            hotel.images = new_image_urls
        else:
            # Append new images (ensure max 3)
            current_images = hotel.images or []
            combined = current_images + new_image_urls
            
            if len(combined) > 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Total images would exceed maximum of 3. Current: {len(current_images)}, Adding: {len(new_image_urls)}"
                )
            
            hotel.images = combined
    
    # Update other fields if provided
    if name is not None:
        hotel.name = name
    if description is not None:
        hotel.description = description
    if address is not None:
        hotel.address = address
    if city is not None:
        hotel.city = city
    if country is not None:
        hotel.country = country
    if phone is not None:
        hotel.phone = phone
    if email is not None:
        hotel.email = email
    if status_field is not None:
        if status_field not in ["active", "inactive", "maintenance"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status must be one of: active, inactive, maintenance"
            )
        hotel.status = status_field
    if is_active is not None:
        hotel.is_active = is_active
    
    db.commit()
    db.refresh(hotel)
    
    return hotel


@router.delete("/{hotel_id}", response_model=MessageResponse)
def delete_hotel(
    hotel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a hotel and all associated room types.
    Also deletes images from Cloudinary.
    """
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    
    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hotel with id {hotel_id} not found"
        )
    
    # Delete images from Cloudinary
    if hotel.images:
        delete_multiple_images(hotel.images)
    
    db.delete(hotel)
    db.commit()
    
    return {
        "message": "Hotel deleted successfully",
        "detail": f"Deleted hotel: {hotel.name}"
    }
