from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Annotated
from datetime import datetime, date
from decimal import Decimal


# ==================== User Schemas ====================

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


# ==================== Hotel Schemas ====================

class HotelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class HotelCreate(HotelBase):
    images: Optional[List[str]] = Field(default=[], max_length=3)
    
    @field_validator('images')
    @classmethod
    def validate_images(cls, v):
        if len(v) > 3:
            raise ValueError('Maximum 3 images allowed')
        return v


class HotelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    images: Optional[List[str]] = Field(None, max_length=3)
    status: Optional[str] = Field(None, pattern="^(active|inactive|maintenance)$")
    is_active: Optional[bool] = None
    
    @field_validator('images')
    @classmethod
    def validate_images(cls, v):
        if v and len(v) > 3:
            raise ValueError('Maximum 3 images allowed')
        return v


class HotelResponse(HotelBase):
    id: int
    images: List[str]
    status: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ==================== Room Type Schemas ====================

class RoomTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    base_rate: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
    max_occupancy: int = Field(default=2, ge=1)
    size_sqm: Optional[int] = Field(None, ge=1)


class RoomTypeCreate(RoomTypeBase):
    hotel_id: int
    images: Optional[List[str]] = Field(default=[], max_length=3)
    
    @field_validator('images')
    @classmethod
    def validate_images(cls, v):
        if len(v) > 3:
            raise ValueError('Maximum 3 images allowed')
        return v


class RoomTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    base_rate: Optional[Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]] = None
    max_occupancy: Optional[int] = Field(None, ge=1)
    size_sqm: Optional[int] = Field(None, ge=1)
    images: Optional[List[str]] = Field(None, max_length=3)
    is_active: Optional[bool] = None
    
    @field_validator('images')
    @classmethod
    def validate_images(cls, v):
        if v and len(v) > 3:
            raise ValueError('Maximum 3 images allowed')
        return v


class RoomTypeResponse(RoomTypeBase):
    id: int
    hotel_id: int
    images: List[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Calculated field for effective rate
    effective_rate: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


# ==================== Rate Adjustment Schemas ====================

class RateAdjustmentBase(BaseModel):
    adjustment_amount: Annotated[Decimal, Field(max_digits=10, decimal_places=2)]
    effective_date: date
    reason: str = Field(..., min_length=1)


class RateAdjustmentCreate(RateAdjustmentBase):
    room_type_id: int
    created_by: Optional[str] = None


class RateAdjustmentResponse(RateAdjustmentBase):
    id: int
    room_type_id: int
    created_by: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Generic Response Schemas ====================

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseModel):
    detail: str
