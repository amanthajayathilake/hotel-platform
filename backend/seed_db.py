"""
Database seeding script to populate initial data.

This script creates:
- Admin user for authentication
- Sample hotels with images
- Sample room types with different rates
- Sample rate adjustments to demonstrate pricing history
"""

from sqlalchemy.orm import Session
from datetime import date, timedelta
from decimal import Decimal

from app.database import SessionLocal, engine
from app.models import User, Hotel, RoomType, RateAdjustment
from app.database import Base
from app.utils.auth import get_password_hash


def seed_database():
    """
    Seed the database with initial data.
    """
    db = SessionLocal()
    
    try:
        print("Starting database seeding...")
        
        # Create admin user
        print("\n1. Creating admin user...")
        admin_user = User(
            email="admin@hotel.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="System Administrator",
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.flush()
        print("✓ Admin user created (username: admin, password: admin123)")
        
        # Create staff user
        staff_user = User(
            email="staff@hotel.com",
            username="staff",
            hashed_password=get_password_hash("staff123"),
            full_name="Staff Member",
            is_active=True,
            is_superuser=False
        )
        db.add(staff_user)
        db.flush()
        print("✓ Staff user created (username: staff, password: staff123)")
        
        # Create sample hotels
        print("\n2. Creating sample hotels...")
        
        hotel1 = Hotel(
            name="Grand Plaza Hotel",
            description="Luxury hotel in the heart of the city with world-class amenities",
            address="123 Main Street",
            city="New York",
            country="USA",
            phone="+1-555-0100",
            email="info@grandplaza.com",
            images=[],  # You can add image URLs here after uploading to Cloudinary
            status="active"
        )
        db.add(hotel1)
        db.flush()
        print(f"✓ Created hotel: {hotel1.name}")
        
        hotel2 = Hotel(
            name="Seaside Resort & Spa",
            description="Beachfront resort with stunning ocean views and spa facilities",
            address="456 Beach Road",
            city="Miami",
            country="USA",
            phone="+1-555-0200",
            email="info@seasideresort.com",
            images=[],
            status="active"
        )
        db.add(hotel2)
        db.flush()
        print(f"✓ Created hotel: {hotel2.name}")
        
        hotel3 = Hotel(
            name="Mountain View Lodge",
            description="Cozy mountain retreat perfect for skiing and hiking",
            address="789 Alpine Drive",
            city="Aspen",
            country="USA",
            phone="+1-555-0300",
            email="info@mountainlodge.com",
            images=[],
            status="maintenance"
        )
        db.add(hotel3)
        db.flush()
        print(f"✓ Created hotel: {hotel3.name}")
        
        # Create room types for Grand Plaza Hotel
        print("\n3. Creating room types...")
        
        # Standard Room
        standard_room = RoomType(
            hotel_id=hotel1.id,
            name="Standard Room",
            description="Comfortable room with queen bed and city view",
            base_rate=Decimal("100.00"),
            max_occupancy=2,
            size_sqm=25,
            images=[]
        )
        db.add(standard_room)
        db.flush()
        print(f"✓ Created room type: {standard_room.name} (Base rate: ${standard_room.base_rate})")
        
        # Deluxe Suite
        deluxe_suite = RoomType(
            hotel_id=hotel1.id,
            name="Deluxe Suite",
            description="Spacious suite with king bed, living area, and panoramic views",
            base_rate=Decimal("250.00"),
            max_occupancy=4,
            size_sqm=60,
            images=[]
        )
        db.add(deluxe_suite)
        db.flush()
        print(f"✓ Created room type: {deluxe_suite.name} (Base rate: ${deluxe_suite.base_rate})")
        
        # Presidential Suite
        presidential_suite = RoomType(
            hotel_id=hotel1.id,
            name="Presidential Suite",
            description="Ultimate luxury suite with multiple bedrooms and private terrace",
            base_rate=Decimal("500.00"),
            max_occupancy=6,
            size_sqm=120,
            images=[]
        )
        db.add(presidential_suite)
        db.flush()
        print(f"✓ Created room type: {presidential_suite.name} (Base rate: ${presidential_suite.base_rate})")
        
        # Create room types for Seaside Resort
        ocean_view = RoomType(
            hotel_id=hotel2.id,
            name="Ocean View Room",
            description="Beautiful room overlooking the ocean",
            base_rate=Decimal("180.00"),
            max_occupancy=2,
            size_sqm=30,
            images=[]
        )
        db.add(ocean_view)
        db.flush()
        print(f"✓ Created room type: {ocean_view.name} (Base rate: ${ocean_view.base_rate})")
        
        beach_villa = RoomType(
            hotel_id=hotel2.id,
            name="Beach Villa",
            description="Private villa with direct beach access",
            base_rate=Decimal("400.00"),
            max_occupancy=4,
            size_sqm=80,
            images=[]
        )
        db.add(beach_villa)
        db.flush()
        print(f"✓ Created room type: {beach_villa.name} (Base rate: ${beach_villa.base_rate})")
        
        # Create rate adjustments with history
        print("\n4. Creating rate adjustment history...")
        
        today = date.today()
        
        # Historical adjustment (30 days ago) - Winter season discount
        adjustment1 = RateAdjustment(
            room_type_id=standard_room.id,
            adjustment_amount=Decimal("-10.00"),
            effective_date=today - timedelta(days=30),
            reason="Winter season discount to boost occupancy",
            created_by="admin"
        )
        db.add(adjustment1)
        print(f"✓ Added adjustment: -$10 (30 days ago) - Winter discount")
        
        # Recent adjustment (7 days ago) - Conference event pricing
        adjustment2 = RateAdjustment(
            room_type_id=standard_room.id,
            adjustment_amount=Decimal("20.00"),
            effective_date=today - timedelta(days=7),
            reason="Major conference in the city - increased demand",
            created_by="admin"
        )
        db.add(adjustment2)
        print(f"✓ Added adjustment: +$20 (7 days ago) - Conference pricing")
        
        # Future adjustment - Holiday season
        adjustment3 = RateAdjustment(
            room_type_id=standard_room.id,
            adjustment_amount=Decimal("50.00"),
            effective_date=today + timedelta(days=30),
            reason="Holiday season premium pricing",
            created_by="admin"
        )
        db.add(adjustment3)
        print(f"✓ Added adjustment: +$50 (30 days from now) - Holiday pricing")
        
        # Deluxe suite adjustments
        adjustment4 = RateAdjustment(
            room_type_id=deluxe_suite.id,
            adjustment_amount=Decimal("30.00"),
            effective_date=today - timedelta(days=7),
            reason="Premium service package included",
            created_by="admin"
        )
        db.add(adjustment4)
        print(f"✓ Added adjustment: +$30 (Deluxe Suite) - Premium package")
        
        # Ocean view adjustment
        adjustment5 = RateAdjustment(
            room_type_id=ocean_view.id,
            adjustment_amount=Decimal("25.00"),
            effective_date=today,
            reason="Peak summer season pricing",
            created_by="staff"
        )
        db.add(adjustment5)
        print(f"✓ Added adjustment: +$25 (Ocean View) - Summer pricing")
        
        # Commit all changes
        db.commit()
        
        print("\n" + "="*60)
        print("✓ Database seeding completed successfully!")
        print("="*60)
        print("\nSeeded data summary:")
        print(f"  - Users: 2 (admin, staff)")
        print(f"  - Hotels: 3")
        print(f"  - Room Types: 5")
        print(f"  - Rate Adjustments: 5")
        print("\nLogin credentials:")
        print("  Admin - username: admin, password: admin123")
        print("  Staff - username: staff, password: staff123")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {str(e)}")
        db.rollback()
        raise
    
    finally:
        db.close()


def reset_database():
    """
    Drop all tables and recreate them.
    USE WITH CAUTION - This will delete all data!
    """
    print("WARNING: This will delete all existing data!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        print("\nDropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✓ All tables dropped")
        
        print("\nCreating all tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created")
        
        return True
    else:
        print("Operation cancelled")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        if reset_database():
            seed_database()
    else:
        seed_database()
