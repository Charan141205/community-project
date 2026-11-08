"""
Main FastAPI application entry point for flood-ews backend.
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.db import db
from backend.app.mqtt_service import mqtt_service
from backend.app.websocket_manager import ws_manager
from backend.app.api.nodes import router as nodes_router
from backend.app.api.alerts import router as alerts_router
from backend.app.api.evacuation import router as evacuation_router
from backend.app.api.subscribers import router as subscribers_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("flood_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize DB connection and background MQTT worker."""
    logger.info("Initializing flood-ews backend services...")
    await db.connect()

    loop = asyncio.get_running_loop()
    mqtt_service.start(loop)

    yield

    logger.info("Shutting down flood-ews backend services...")
    mqtt_service.stop()
    await db.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    description="Smart Community Flood & Urban Drainage Early Warning System API",
    version="1.0.0",
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
        # Send initial welcome payload
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to flood-ews live stream",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # Keep connection alive; accept client messages/pings
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        await ws_manager.disconnect(websocket)
