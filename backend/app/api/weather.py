"""
Weather API Router.
Provides current precipitation readings and 6-hour predictive forecasts for Hyderabad.
"""

from fastapi import APIRouter, Query
from backend.app.weather import fetch_weather_forecast

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/forecast")
async def get_forecast(
    refresh: bool = Query(False, description="Force refresh from external meteorological API"),
):
    """Retrieve 6-hour precipitation forecast and storm inbound alerts."""
    return await fetch_weather_forecast(force_refresh=refresh)
