"""
Citizen Subscribers API Router.
Enables citizens to opt in to early warning SMS/WhatsApp alerts.
"""

from fastapi import APIRouter, status

from backend.app.db import db
from backend.app.schemas import SubscriberCreate, SubscriberResponse

router = APIRouter(prefix="/api/subscribers", tags=["subscribers"])


@router.post("", response_model=SubscriberResponse, status_code=status.HTTP_201_CREATED)
async def register_subscriber(sub: SubscriberCreate):
    """Register or update citizen notification preferences (English, Telugu, or Hindi)."""
    record = await db.add_subscriber(
        phone=sub.phone,
        name=sub.name,
        ward=sub.ward,
        language=sub.language,
        opted_in=sub.opted_in,
    )
    return SubscriberResponse(
        id=record["id"],
        phone=record["phone"],
        name=record["name"],
        ward=record["ward"],
        language=record["language"],
        opted_in=record["opted_in"],
        created_at=record["created_at"],
    )
