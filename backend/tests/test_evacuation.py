"""
Unit tests for the Evacuation Router:
Shortest path routing, nearest shelter selection with capacity,
and dynamic 300m flood obstacle avoidance (penalizing WARNING, pruning CRITICAL).
"""

import pytest
from backend.app.evacuation import EvacuationRouter, haversine_distance_m


def test_haversine_distance():
    # Distance between Kapilatheertham (13.6508, 79.4215) and Leela Mahal (13.6370, 79.4285)
    dist = haversine_distance_m(13.6508, 79.4215, 13.6370, 79.4285)
    # Approx 1.7 km
    assert 1500 < dist < 1900


def test_evacuation_routing_normal():
    router = EvacuationRouter()

    shelters = [
        {"id": "s1", "name": "Mahati Community Relief Centre", "lat": 13.6295, "lon": 79.4200, "capacity": 350, "current_occupancy": 15},
        {"id": "s2", "name": "SV High School & Relief Camp", "lat": 13.6410, "lon": 79.4120, "capacity": 450, "current_occupancy": 42},
    ]

    # Origin near Kapilatheertham
    origin_lat, origin_lon = 13.6500, 79.4210

    result = router.route_to_nearest_shelter(
        origin_lat=origin_lat,
        origin_lon=origin_lon,
        shelters=shelters,
        flooded_nodes=[],
    )

    assert result is not None
    assert result["distance_km"] > 0
    assert result["eta_minutes"] > 0
    assert result["geojson"]["type"] == "Feature"
    assert result["geojson"]["geometry"]["type"] == "LineString"
    assert len(result["geojson"]["geometry"]["coordinates"]) >= 3


def test_evacuation_avoids_critical_flood_nodes():
    router = EvacuationRouter()

    shelters = [
        {"id": "s1", "name": "Mahati Relief Centre", "lat": 13.6295, "lon": 79.4200, "capacity": 300, "current_occupancy": 10},
    ]

    # Road passing near Railway Underbridge (13.6255, 79.4205)
    flooded_nodes = [
        {"id": "drain-03", "name": "Railway Underbridge (West)", "lat": 13.6255, "lon": 79.4205, "risk_level": "CRITICAL"},
    ]

    dynamic_graph, avoided_ids = router.build_dynamic_graph(flooded_nodes, avoidance_radius_m=300.0)

    # Verify that drain-03 was detected and avoided
    assert "drain-03" in avoided_ids
