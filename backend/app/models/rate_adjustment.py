from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class RateAdjustment(Base):
    """
    Rate adjustment model for tracking price changes over time.
    Stores historical price adjustments with reasons and effective dates.
    
    Logic: effective_rate = base_rate + adjustment_amount
    The latest adjustment with effective_date <= today is applied.
    """
    __tablename__ = "rate_adjustments"
    
    id = Column(Integer, primary_key=True, index=True)
    room_type_id = Column(Integer, ForeignKey("room_types.id", ondelete="CASCADE"), nullable=False)
    
    # Adjustment amount (can be positive or negative)
    adjustment_amount = Column(Numeric(10, 2), nullable=False)
    
    # When this adjustment becomes effective
    effective_date = Column(Date, nullable=False, index=True)
    
    # Reason for the adjustment
    reason = Column(Text, nullable=False)
    
    # Who made this adjustment
    created_by = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    room_type = relationship("RoomType", back_populates="rate_adjustments")
    
    def __repr__(self):
        return f"<RateAdjustment(amount={self.adjustment_amount}, effective_date={self.effective_date})>"
