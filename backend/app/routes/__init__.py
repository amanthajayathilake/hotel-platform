from app.routes.auth import router as auth_router
from app.routes.hotels import router as hotels_router
from app.routes.room_types import router as room_types_router
from app.routes.rate_adjustments import router as rate_adjustments_router

__all__ = [
    "auth_router",
    "hotels_router",
    "room_types_router",
    "rate_adjustments_router"
]
