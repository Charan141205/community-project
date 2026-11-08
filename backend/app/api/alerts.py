"""
Alerts API Router.
Provides recent disaster early warning alerts and notification audit history.
"""

from typing import List
from fastapi import APIRouter, Query

from backend.app.db import db
from backend.app.schemas import AlertResponse

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    limit: int = Query(50, ge=1, le=200, description="Max alerts to return"),
):
    """Retrieve newest early warning alerts sent to citizens and disaster response teams."""
    records = await db.get_alerts(limit=limit)
    return [
        AlertResponse(
            id=r["id"],
            node_id=r["node_id"],
            level=r["level"],
            message=r["message"],
            channel=r["channel"],
            sent_at=r["sent_at"],
            recipients_count=r.get("recipients_count", 0),
        )
        for r in records
    ]
