"""
Unit tests for the Evacuation Router:
Shortest path routing, nearest shelter selection with capacity,
and dynamic 300m flood obstacle avoidance (penalizing WARNING, pruning CRITICAL).
"""

import pytest
from backend.app.evacuation import EvacuationRouter, haversine_distance_m


def test_haversine_distance():
    # Distance between Moosarambagh (17.3705, 78.5080) and Chaderghat (17.3789, 78.4902)
    dist = haversine_distance_m(17.3705, 78.5080, 17.3789, 78.4902)
    # Approx 2.1 km
    assert 1800 < dist < 2400


def test_evacuation_routing_normal():
    router = EvacuationRouter()

    shelters = [
        {"id": "s1", "name": "Nimboliadda Community Hall", "lat": 17.3820, "lon": 78.4950, "capacity": 200, "current_occupancy": 20},
        {"id": "s2", "name": "Amberpet Indoor Stadium", "lat": 17.3980, "lon": 78.5150, "capacity": 400, "current_occupancy": 50},
    ]

    # Origin at Moosarambagh
    origin_lat, origin_lon = 17.3710, 78.5085

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
        {"id": "s1", "name": "Chaderghat School", "lat": 17.3760, "lon": 78.4870, "capacity": 300, "current_occupancy": 10},
    ]

    # Road passing near Malakpet (17.3750, 78.4985)
    flooded_nodes = [
        {"id": "drain-06", "name": "Malakpet Underpass", "lat": 17.3750, "lon": 78.4985, "risk_level": "CRITICAL"},
    ]

    dynamic_graph, avoided_ids = router.build_dynamic_graph(flooded_nodes, avoidance_radius_m=300.0)

    # Verify that drain-06 was detected and avoided
    assert "drain-06" in avoided_ids
