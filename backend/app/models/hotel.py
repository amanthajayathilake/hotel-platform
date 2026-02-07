from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Hotel(Base):
    """
    Hotel model representing individual hotel properties.
    Each hotel can have multiple room types and images.
    """
    __tablename__ = "hotels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    address = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Store image URLs as JSON array (max 3 images)
    images = Column(JSON, default=list)
    
    # Status field - added in second migration
    status = Column(String(20), default="active")  # active, inactive, maintenance
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    room_types = relationship("RoomType", back_populates="hotel", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Hotel(name='{self.name}', city='{self.city}')>"
