"""
Async Database layer for flood-ews.
Provides connection pooling for TimescaleDB / PostgreSQL via asyncpg,
with an in-memory synchronized store for seamless local execution & testing.
"""

import asyncio
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
import asyncpg
from backend.app.config import settings

logger = logging.getLogger("flood_db")

# In-memory store fallback & fast cache (Tirupati Region)
IN_MEMORY_NODES: Dict[str, Dict[str, Any]] = {
    "drain-01": {"id": "drain-01", "name": "Kapilatheertham Nallah", "lat": 13.6508, "lon": 79.4215, "ward": "Alipiri", "mount_height_cm": 200.0, "capacity_cm": 180.0, "status": "online", "current_gate_deg": 0, "last_seen": datetime.now(timezone.utc)},
    "drain-02": {"id": "drain-02", "name": "Leela Mahal Culvert", "lat": 13.6370, "lon": 79.4285, "ward": "Korlagunta", "mount_height_cm": 220.0, "capacity_cm": 200.0, "status": "online", "current_gate_deg": 0, "last_seen": datetime.now(timezone.utc)},
    "drain-03": {"id": "drain-03", "name": "Railway Underbridge (West)", "lat": 13.6255, "lon": 79.4205, "ward": "Tata Nagar", "mount_height_cm": 180.0, "capacity_cm": 150.0, "status": "online", "current_gate_deg": 0, "last_seen": datetime.now(timezone.utc)},
    "drain-04": {"id": "drain-04", "name": "Korlagunta Storm Canal", "lat": 13.6330, "lon": 79.4350, "ward": "Korlagunta", "mount_height_cm": 210.0, "capacity_cm": 190.0, "status": "online", "current_gate_deg": 0, "last_seen": datetime.now(timezone.utc)},
    "drain-05": {"id": "drain-05", "name": "Alipiri Footpath Channel", "lat": 13.6450, "lon": 79.4070, "ward": "Alipiri", "mount_height_cm": 190.0, "capacity_cm": 160.0, "status": "online", "current_gate_deg": 0, "last_seen": datetime.now(timezone.utc)},
    "drain-06": {"id": "drain-06", "name": "Tiruchanur Swarnamukhi Causeway", "lat": 13.6095, "lon": 79.4505, "ward": "Tiruchanur", "mount_height_cm": 230.0, "capacity_cm": 210.0, "status": "online", "current_gate_deg": 0, "last_seen": datetime.now(timezone.utc)},
}

IN_MEMORY_SHELTERS: List[Dict[str, Any]] = [
    {"id": "shelter-01", "name": "SV High School & Relief Camp", "lat": 13.6410, "lon": 79.4120, "capacity": 450, "current_occupancy": 42, "ward": "Alipiri", "contact_phone": "+91-877-2287111"},
    {"id": "shelter-02", "name": "Mahati Community Relief Centre", "lat": 13.6295, "lon": 79.4200, "capacity": 350, "current_occupancy": 15, "ward": "Tata Nagar", "contact_phone": "+91-877-2264222"},
    {"id": "shelter-03", "name": "Municipal High School Korlagunta", "lat": 13.6350, "lon": 79.4310, "capacity": 300, "current_occupancy": 20, "ward": "Korlagunta", "contact_phone": "+91-877-2245333"},
    {"id": "shelter-04", "name": "SV University Indoor Stadium Relief Camp", "lat": 13.6320, "lon": 79.4005, "capacity": 500, "current_occupancy": 30, "ward": "SVU Campus", "contact_phone": "+91-877-2248444"},
]

IN_MEMORY_SUBSCRIBERS: List[Dict[str, Any]] = [
    {"id": 1, "phone": "+919876543210", "name": "K. Venkataswamy", "ward": "Alipiri", "language": "te", "opted_in": True, "created_at": datetime.now(timezone.utc)},
    {"id": 2, "phone": "+919876543211", "name": "Sujata Sharma", "ward": "Korlagunta", "language": "hi", "opted_in": True, "created_at": datetime.now(timezone.utc)},
    {"id": 3, "phone": "+919876543212", "name": "Dr. K. Srinivas", "ward": "Tata Nagar", "language": "en", "opted_in": True, "created_at": datetime.now(timezone.utc)},
    {"id": 4, "phone": "+919876543213", "name": "Lakshmi Devi", "ward": "Alipiri", "language": "te", "opted_in": True, "created_at": datetime.now(timezone.utc)},
    {"id": 5, "phone": "+919876543214", "name": "Rajesh Varma", "ward": "Tiruchanur", "language": "hi", "opted_in": True, "created_at": datetime.now(timezone.utc)},
]

IN_MEMORY_READINGS: List[Dict[str, Any]] = []
IN_MEMORY_ALERTS: List[Dict[str, Any]] = []
IN_MEMORY_GATE_LOGS: List[Dict[str, Any]] = []


class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.is_connected = False

    async def connect(self):
        """Initialize asyncpg connection pool to TimescaleDB / PostgreSQL."""
        try:
            self.pool = await asyncpg.create_pool(
                dsn=settings.DATABASE_URL,
                min_size=settings.DB_POOL_MIN_SIZE,
                max_size=settings.DB_POOL_MAX_SIZE,
                timeout=5.0,
            )
            self.is_connected = True
            logger.info("Connected to PostgreSQL/TimescaleDB connection pool.")
        except Exception as e:
            logger.warning(f"Could not connect to database at {settings.DATABASE_URL}: {e}. Operating with in-memory store.")
            self.is_connected = False

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self.is_connected = False
            logger.info("Database connection pool closed.")

    async def get_all_nodes(self) -> List[Dict[str, Any]]:
        if self.is_connected and self.pool:
            try:
                async with self.pool.acquire() as conn:
                    rows = await conn.fetch("SELECT * FROM nodes ORDER BY id ASC")
                    return [dict(r) for r in rows]
            except Exception as e:
                logger.error(f"DB error fetching nodes: {e}")
        return list(IN_MEMORY_NODES.values())

    async def get_node_by_id(self, node_id: str) -> Optional[Dict[str, Any]]:
        if self.is_connected and self.pool:
            try:
                async with self.pool.acquire() as conn:
                    row = await conn.fetchrow("SELECT * FROM nodes WHERE id = $1", node_id)
                    return dict(row) if row else None
            except Exception as e:
                logger.error(f"DB error fetching node {node_id}: {e}")
        return IN_MEMORY_NODES.get(node_id)

    async def update_node_status(self, node_id: str, status: str, gate_deg: Optional[int] = None):
        now = datetime.now(timezone.utc)
        if node_id in IN_MEMORY_NODES:
            IN_MEMORY_NODES[node_id]["status"] = status
            IN_MEMORY_NODES[node_id]["last_seen"] = now
            if gate_deg is not None:
                IN_MEMORY_NODES[node_id]["current_gate_deg"] = gate_deg

        if self.is_connected and self.pool:
            try:
                async with self.pool.acquire() as conn:
                    if gate_deg is not None:
                        await conn.execute(
                            "UPDATE nodes SET status = $1, last_seen = $2, current_gate_deg = $3 WHERE id = $4",
                            status, now, gate_deg, node_id
                        )
                    else:
                        await conn.execute(
                            "UPDATE nodes SET status = $1, last_seen = $2 WHERE id = $3",
                            status, now, node_id
                        )
            except Exception as e:
                logger.error(f"DB error updating node status {node_id}: {e}")

    async def insert_reading(self, reading: Dict[str, Any]):
        IN_MEMORY_READINGS.append(reading)
        # Keep recent 1000 readings in memory
        if len(IN_MEMORY_READINGS) > 1000:
            IN_MEMORY_READINGS.pop(0)

        # Update node current gate degree
        node_id = reading["node_id"]
        if node_id in IN_MEMORY_NODES:
            IN_MEMORY_NODES[node_id]["current_gate_deg"] = reading.get("gate_deg", 0)
            IN_MEMORY_NODES[node_id]["last_seen"] = reading["time"]

        if self.is_connected and self.pool:
            try:
                async with self.pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO readings (time, node_id, depth_cm, rain_mm_h, gate_deg, rssi)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        """,
                        reading["time"], reading["node_id"], reading["depth_cm"],
                        reading["rain_mm_h"], reading["gate_deg"], reading["rssi"]
                    )
            except Exception as e:
                logger.error(f"DB error inserting reading for {node_id}: {e}")

    async def get_node_readings(self, node_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        if self.is_connected and self.pool:
            try:
                async with self.pool.acquire() as conn:
                    rows = await conn.fetch(
                        "SELECT * FROM readings WHERE node_id = $1 ORDER BY time DESC LIMIT $2",
                        node_id, limit
                    )
                    return [dict(r) for r in reversed(rows)]
            except Exception as e:
                logger.error(f"DB error fetching readings for {node_id}: {e}")

        # In-memory filter
        filtered = [r for r in IN_MEMORY_READINGS if r.get("node_id") == node_id]
        return filtered[-limit:]

    async def insert_alert(self, node_id: str, level: str, message: str, channel: str, recipients_count: int) -> int:
        now = datetime.now(timezone.utc)
        alert_id = len(IN_MEMORY_ALERTS) + 1
        record = {
            "id": alert_id,
            "node_id": node_id,
            "level": level,
            "message": message,
            "channel": channel,
            "sent_at": now,
            "recipients_count": recipients_count,
        }
        IN_MEMORY_ALERTS.insert(0, record)

        if self.is_connected and self.pool:
            try:
                async with self.pool.acquire() as conn:
                    row = await conn.fetchrow(
                        """
                        INSERT INTO alerts (node_id, level, message, channel, sent_at, recipients_count)
                        VALUES ($1, $2, $3, $4, $5, $6) RETURNING id
                        """,
                        node_id, level, message, channel, now, recipients_count
                    )
                    if row:
                        return row["id"]
            except Exception as e:
                logger.error(f"DB error inserting alert: {e}")
        return alert_id

    async def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        if self.is_connected and self.pool:
            try:
                async with self.pool.acquire() as conn:
                    rows = await conn.fetch("SELECT * FROM alerts ORDER BY sent_at DESC LIMIT $1", limit)
                    return [dict(r) for r in rows]
            except Exception as e:
                logger.error(f"DB error fetching alerts: {e}")
        return IN_MEMORY_ALERTS[:limit]

    async def log_gate_action(self, node_id: str, gate_angle: int, reason: str, triggered_by: str):
        now = datetime.now(timezone.utc)
        record = {
            "id": len(IN_MEMORY_GATE_LOGS) + 1,
            "node_id": node_id,
            "gate_angle": gate_angle,
            "reason": reason,
            "triggered_by": triggered_by,
            "created_at": now,
        }
        IN_MEMORY_GATE_LOGS.insert(0, record)
        if node_id in IN_MEMORY_NODES:
            IN_MEMORY_NODES[node_id]["current_gate_deg"] = gate_angle

        if self.is_connected and self.pool:
            try:
                async with self.pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO gate_audit_logs (node_id, gate_angle, reason, triggered_by, created_at)
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        node_id, gate_angle, reason, triggered_by, now
                    )
                    await conn.execute("UPDATE nodes SET current_gate_deg = $1 WHERE id = $2", gate_angle, node_id)
            except Exception as e:
                logger.error(f"DB error logging gate action for {node_id}: {e}")

    async def get_shelters(self) -> List[Dict[str, Any]]:
        if self.is_connected and self.pool:
            try:
                async with self.pool.acquire() as conn:
                    rows = await conn.fetch("SELECT * FROM shelters ORDER BY id ASC")
                    return [dict(r) for r in rows]
            except Exception as e:
                logger.error(f"DB error fetching shelters: {e}")
        return IN_MEMORY_SHELTERS

    async def get_subscribers_by_ward(self, ward: str) -> List[Dict[str, Any]]:
        if self.is_connected and self.pool:
            try:
                async with self.pool.acquire() as conn:
                    rows = await conn.fetch("SELECT * FROM subscribers WHERE ward = $1 AND opted_in = TRUE", ward)
                    return [dict(r) for r in rows]
            except Exception as e:
                logger.error(f"DB error fetching subscribers for ward {ward}: {e}")
        return [s for s in IN_MEMORY_SUBSCRIBERS if s.get("ward") == ward and s.get("opted_in", True)]

    async def add_subscriber(self, phone: str, name: str, ward: str, language: str, opted_in: bool = True) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        sub_id = len(IN_MEMORY_SUBSCRIBERS) + 1
        record = {
            "id": sub_id,
            "phone": phone,
            "name": name,
            "ward": ward,
            "language": language,
            "opted_in": opted_in,
            "created_at": now,
        }
        IN_MEMORY_SUBSCRIBERS.append(record)

        if self.is_connected and self.pool:
            try:
                async with self.pool.acquire() as conn:
                    row = await conn.fetchrow(
                        """
                        INSERT INTO subscribers (phone, name, ward, language, opted_in, created_at)
                        VALUES ($1, $2, $3, $4, $5, $6)
                        ON CONFLICT (phone) DO UPDATE SET
                            name = EXCLUDED.name,
                            ward = EXCLUDED.ward,
                            language = EXCLUDED.language,
                            opted_in = EXCLUDED.opted_in
                        RETURNING id, phone, name, ward, language, opted_in, created_at
                        """,
                        phone, name, ward, language, opted_in, now
                    )
                    if row:
                        return dict(row)
            except Exception as e:
                logger.error(f"DB error adding subscriber: {e}")
        return record


# Global Database instance
db = Database()
