from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class RoomType(Base):
    """
    Room type model for different categories of rooms in a hotel.
    Stores base pricing and room specifications.
    """
    __tablename__ = "room_types"
    
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Base rate in USD (or your preferred currency)
    base_rate = Column(Numeric(10, 2), nullable=False)
    
    # Room specifications
    max_occupancy = Column(Integer, default=2)
    size_sqm = Column(Integer, nullable=True)
    
    # Store image URLs as JSON array (max 3 images)
    images = Column(JSON, default=list)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    hotel = relationship("Hotel", back_populates="room_types")
    rate_adjustments = relationship("RateAdjustment", back_populates="room_type", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RoomType(name='{self.name}', base_rate={self.base_rate})>"
