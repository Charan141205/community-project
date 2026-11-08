"""
Main FastAPI application entry point for flood-ews backend.
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.db import db
from backend.app.mqtt_service import mqtt_service
from backend.app.weather import fetch_weather_forecast
from backend.app.websocket_manager import ws_manager
from backend.app.api.nodes import router as nodes_router
from backend.app.api.alerts import router as alerts_router
from backend.app.api.evacuation import router as evacuation_router
from backend.app.api.subscribers import router as subscribers_router
from backend.app.api.weather import router as weather_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("flood_app")

weather_task = None


async def periodic_weather_poller():
    """Background task refreshing precipitation forecasts every 30 minutes."""
    while True:
        try:
            if settings.PREDICTIVE_WEATHER_ENABLED:
                forecast = await fetch_weather_forecast(force_refresh=True)
                if forecast.get("storm_inbound"):
                    logger.warning("🚨 PREDICTIVE ALERT: Severe storm forecasted in the next hour!")
                    await ws_manager.broadcast({
                        "type": "weather_alert",
                        "data": forecast,
                    })
        except Exception as e:
            logger.warning(f"Error in weather polling loop: {e}")
        await asyncio.sleep(settings.WEATHER_CACHE_MINUTES * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize DB connection, background MQTT worker, and weather poller."""
    global weather_task
    logger.info("Initializing flood-ews backend services...")
    await db.connect()

    loop = asyncio.get_running_loop()
    mqtt_service.start(loop)

    # Launch background predictive weather poller
    weather_task = asyncio.create_task(periodic_weather_poller())

    yield

    logger.info("Shutting down flood-ews backend services...")
    if weather_task:
        weather_task.cancel()
    mqtt_service.stop()
    await db.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    description="Smart Community Flood & Urban Drainage Early Warning System API",
    version="1.1.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(nodes_router)
app.include_router(alerts_router)
app.include_router(evacuation_router)
app.include_router(subscribers_router)
app.include_router(weather_router)


@app.get("/health")
async def health_check():
    """Health check endpoint verifying DB connection and MQTT service status."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected" if db.is_connected else "in_memory_fallback",
        "mqtt_broker": "connected" if mqtt_service.is_connected else "disconnected",
        "predictive_weather": "enabled" if settings.PREDICTIVE_WEATHER_ENABLED else "disabled",
    }


@app.get("/")
async def root():
    return {
        "message": "Welcome to flood-ews: Smart Community Flood & Urban Drainage Early Warning System",
        "docs": "/docs",
        "health": "/health",
        "ws_stream": "/ws/live",
    }


@app.websocket("/ws/live")
async def websocket_live_stream(websocket: WebSocket):
    """Live WebSocket stream pushing real-time telemetry updates and alerts."""
    await ws_manager.connect(websocket)
    try:
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to flood-ews live stream",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        await ws_manager.disconnect(websocket)
