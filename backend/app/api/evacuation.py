"""
Evacuation Routing API Router.
Calculates optimal evacuation path to nearest available shelter avoiding flooded channels.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, Query

from backend.app.db import db
from backend.app.evacuation import evacuation_router
from backend.app.mqtt_service import get_or_create_tracker
from backend.app.schemas import EvacuationRoute, ShelterResponse

router = APIRouter(prefix="/api/evacuation", tags=["evacuation"])


@router.get("", response_model=EvacuationRoute)
async def get_evacuation_route(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Citizen/Vehicle Latitude"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Citizen/Vehicle Longitude"),
):
    """
    Compute dynamic evacuation route from citizen coordinates to the nearest shelter.
    Avoids road segments within 300 meters of nodes at WARNING (heavily penalized) or CRITICAL (blocked).
    """
    nodes = await db.get_all_nodes()
    flooded_nodes: List[Dict[str, Any]] = []

    for n in nodes:
        tracker = get_or_create_tracker(n["id"], n.get("capacity_cm", 180.0))
        risk_label = tracker.current_level.label
        flooded_nodes.append({
            "id": n["id"],
            "name": n["name"],
            "lat": n["lat"],
            "lon": n["lon"],
            "risk_level": risk_label,
        })

    shelters = await db.get_shelters()

    result = evacuation_router.route_to_nearest_shelter(
        origin_lat=lat,
        origin_lon=lon,
        shelters=shelters,
        flooded_nodes=flooded_nodes,
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Unable to find a viable evacuation route. Please move to higher ground immediately.",
        )

    shelter_data = result["shelter"]
    return EvacuationRoute(
        shelter=ShelterResponse(
            id=shelter_data["id"],
            name=shelter_data["name"],
            lat=shelter_data["lat"],
            lon=shelter_data["lon"],
            capacity=shelter_data["capacity"],
            current_occupancy=shelter_data.get("current_occupancy", 0),
            ward=shelter_data.get("ward", "General"),
            contact_phone=shelter_data.get("contact_phone"),
        ),
        distance_km=result["distance_km"],
        eta_minutes=result["eta_minutes"],
        avoided_flooded_nodes=result["avoided_flooded_nodes"],
        geojson=result["geojson"],
    )
