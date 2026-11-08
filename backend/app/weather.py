"""
Predictive Weather Forecasting Engine.
Queries Open-Meteo meteorological API for hourly precipitation forecasts,
providing pre-emptive flood watch triggers for Tirupati's Swarnamukhi River & Seshachalam hill catchment basin.
"""

from datetime import datetime, timezone
import logging
import time
from typing import Any, Dict, Optional
import httpx
from backend.app.config import settings

logger = logging.getLogger("flood_weather")

# In-memory cache
_weather_cache: Optional[Dict[str, Any]] = None
_last_fetch_ts: float = 0.0


async def fetch_weather_forecast(force_refresh: bool = False) -> Dict[str, Any]:
    """
    Fetch precipitation forecast for the next 6 hours from Open-Meteo API.
    Caches result for `settings.WEATHER_CACHE_MINUTES` (default 30 mins).
    """
    global _weather_cache, _last_fetch_ts

    now = time.time()
    cache_ttl = settings.WEATHER_CACHE_MINUTES * 60

    if not force_refresh and _weather_cache and (now - _last_fetch_ts < cache_ttl):
        return _weather_cache

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={settings.WEATHER_API_LAT}&longitude={settings.WEATHER_API_LON}"
        f"&hourly=precipitation,rain,weather_code&forecast_hours=6&timezone=auto"
    )

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                hourly = data.get("hourly", {})
                precip_list = hourly.get("precipitation", [])
                time_list = hourly.get("time", [])

                max_rain_1h = precip_list[0] if len(precip_list) > 0 else 0.0
                max_rain_3h = max(precip_list[:3]) if len(precip_list) >= 3 else max_rain_1h

                is_storm_inbound = max_rain_1h >= settings.PREDICTIVE_RAIN_WATCH_THRESHOLD

                _weather_cache = {
                    "source": "Open-Meteo Meteorological Service",
                    "latitude": settings.WEATHER_API_LAT,
                    "longitude": settings.WEATHER_API_LON,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "current_precipitation_mm_h": float(max_rain_1h),
                    "max_forecast_3h_mm_h": float(max_rain_3h),
                    "storm_inbound": bool(is_storm_inbound),
                    "forecast_timeline": [
                        {"time": time_list[i], "precipitation_mm_h": precip_list[i]}
                        for i in range(min(len(time_list), 6))
                    ],
                }
                _last_fetch_ts = now
                logger.info(
                    f"🌤️ Updated weather forecast: Max 1h={max_rain_1h:.1f} mm/h | Storm Inbound={is_storm_inbound}"
                )
                return _weather_cache
            else:
                logger.warning(f"Weather API error {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.warning(f"Could not connect to external weather API: {e}. Using baseline forecast.")

    # Fallback response
    if not _weather_cache:
        _weather_cache = {
            "source": "Fallback Offline Forecast",
            "latitude": settings.WEATHER_API_LAT,
            "longitude": settings.WEATHER_API_LON,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "current_precipitation_mm_h": 0.0,
            "max_forecast_3h_mm_h": 0.0,
            "storm_inbound": False,
            "forecast_timeline": [],
        }
    return _weather_cache


def get_cached_forecast_rain_1h() -> float:
    """Get the current cached 1-hour forecasted precipitation rate in mm/h."""
    if _weather_cache:
        return float(_weather_cache.get("current_precipitation_mm_h", 0.0))
    return 0.0
