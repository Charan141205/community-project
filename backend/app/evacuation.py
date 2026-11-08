"""
Dynamic Evacuation Routing Engine.
Computes safe evacuation routes to the nearest available shelter,
dynamically penalizing or pruning road segments within 300m of flooded nodes (WARNING/CRITICAL).
Uses NetworkX with local cached road graph and optional OSMnx enhancement.
"""

import json
import logging
import math
import os
from typing import Any, Dict, List, Optional, Tuple
import networkx as nx

logger = logging.getLogger("evacuation_router")

# ============================================================================
# HAVERSINE DISTANCE HELPERS
# ============================================================================
def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in meters between two coordinates."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def distance_point_to_segment_m(
    p_lat: float, p_lon: float,
    a_lat: float, a_lon: float,
    b_lat: float, b_lon: float
) -> float:
    """Calculate minimum distance from point P to segment A-B in meters."""
    # Approximate planar projection using midpoint latitude
    mid_lat = math.radians((a_lat + b_lat) / 2.0)
    kx = 111320.0 * math.cos(mid_lat)
    ky = 110540.0

    px, py = p_lon * kx, p_lat * ky
    ax, ay = a_lon * kx, a_lat * ky
    bx, by = b_lon * kx, b_lat * ky

    dx, dy = bx - ax, by - ay
    seg_len_sq = dx * dx + dy * dy

    if seg_len_sq == 0:
        return math.hypot(px - ax, py - ay)

    # Project point onto segment
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / seg_len_sq))
    proj_x = ax + t * dx
    proj_y = ay + t * dy

    return math.hypot(px - proj_x, py - proj_y)


# ============================================================================
# TIRUPATI SWARNAMUKHI BASIN & URBAN ROAD NETWORK (Fallback / Fast Graph)
# ============================================================================
DEFAULT_NETWORK = {
    "nodes": {
        "j_kapilatheertham":   {"lat": 13.6508, "lon": 79.4215, "name": "Kapilatheertham Circle"},
        "j_alipiri":           {"lat": 13.6450, "lon": 79.4070, "name": "Alipiri Gateway"},
        "j_balaji_colony":     {"lat": 13.6390, "lon": 79.4150, "name": "Balaji Colony Circle"},
        "j_leelamahal":        {"lat": 13.6370, "lon": 79.4285, "name": "Leela Mahal Junction"},
        "j_korlagunta":        {"lat": 13.6330, "lon": 79.4350, "name": "Korlagunta Crossroads"},
        "j_rtc_bus_stand":     {"lat": 13.6275, "lon": 79.4220, "name": "RTC Central Bus Station"},
        "j_railway_underpass": {"lat": 13.6255, "lon": 79.4205, "name": "Railway Underbridge West"},
        "j_sv_university":     {"lat": 13.6315, "lon": 79.4020, "name": "SV University Main Gate"},
        "j_bairagipatteda":    {"lat": 13.6175, "lon": 79.4260, "name": "Bairagipatteda Circle"},
        "j_air_bypass":        {"lat": 13.6210, "lon": 79.4340, "name": "AIR Bypass Road Junction"},
        "j_renigunta_rd":      {"lat": 13.6280, "lon": 79.4420, "name": "Renigunta Road X Roads"},
        "j_tiruchanur":        {"lat": 13.6105, "lon": 79.4510, "name": "Tiruchanur Causeway Gate"},
    },
    "edges": [
        ("j_alipiri", "j_kapilatheertham",   {"name": "Alipiri Link Road", "speed_kmh": 35}),
        ("j_alipiri", "j_balaji_colony",     {"name": "SV High School Approach", "speed_kmh": 35}),
        ("j_kapilatheertham", "j_leelamahal", {"name": "Kapila Theertham Road", "speed_kmh": 35}),
        ("j_balaji_colony", "j_leelamahal",   {"name": "Balaji Colony Road", "speed_kmh": 30}),
        ("j_balaji_colony", "j_sv_university", {"name": "University Road", "speed_kmh": 35}),
        ("j_sv_university", "j_railway_underpass", {"name": "Station Road West", "speed_kmh": 35}),
        ("j_leelamahal", "j_korlagunta",     {"name": "Korlagunta Main Road", "speed_kmh": 30}),
        ("j_korlagunta", "j_renigunta_rd",   {"name": "Renigunta Highway", "speed_kmh": 45}),
        ("j_leelamahal", "j_rtc_bus_stand",   {"name": "Tilak Road", "speed_kmh": 30}),
        ("j_rtc_bus_stand", "j_railway_underpass", {"name": "Gandhi Road", "speed_kmh": 25}),
        ("j_railway_underpass", "j_bairagipatteda", {"name": "Tata Nagar Avenue", "speed_kmh": 35}),
        ("j_bairagipatteda", "j_air_bypass",  {"name": "Bairagipatteda Arterial", "speed_kmh": 40}),
        ("j_korlagunta", "j_air_bypass",      {"name": "AIR Bypass Link", "speed_kmh": 40}),
        ("j_air_bypass", "j_tiruchanur",      {"name": "Swarnamukhi River Road", "speed_kmh": 45}),
        ("j_renigunta_rd", "j_tiruchanur",    {"name": "Tiruchanur Highway Link", "speed_kmh": 45}),
    ],
}


class EvacuationRouter:
    """High-performance road graph router with dynamic flood avoidance."""

    def __init__(self):
        self.base_graph = nx.Graph()
        self._build_base_graph()

    def _build_base_graph(self):
        """Construct NetworkX graph with geographical lengths."""
        nodes = DEFAULT_NETWORK["nodes"]
        edges = DEFAULT_NETWORK["edges"]

        for n_id, data in nodes.items():
            self.base_graph.add_node(n_id, lat=data["lat"], lon=data["lon"], name=data["name"])

        for u, v, attrs in edges:
            u_data = nodes[u]
            v_data = nodes[v]
            length_m = haversine_distance_m(u_data["lat"], u_data["lon"], v_data["lat"], v_data["lon"])
            speed_kmh = attrs.get("speed_kmh", 30)
            base_time_sec = (length_m / 1000.0) / speed_kmh * 3600.0

            self.base_graph.add_edge(
                u, v,
                length_m=length_m,
                base_time_sec=base_time_sec,
                name=attrs.get("name", "Road"),
                u_coord=(u_data["lat"], u_data["lon"]),
                v_coord=(v_data["lat"], v_data["lon"]),
            )

    def find_nearest_node(self, lat: float, lon: float) -> str:
        """Find the nearest graph intersection to given coordinate."""
        best_node = None
        min_dist = float("inf")
        for node, data in self.base_graph.nodes(data=True):
            dist = haversine_distance_m(lat, lon, data["lat"], data["lon"])
            if dist < min_dist:
                min_dist = dist
                best_node = node
        return best_node

    def build_dynamic_graph(
        self,
        flooded_nodes: List[Dict[str, Any]],
        avoidance_radius_m: float = 300.0
    ) -> Tuple[nx.Graph, List[str]]:
        """
        Create a runtime copy of the road graph:
        - If a road segment is within 300m of a CRITICAL node: REMOVE edge (submerged).
        - If a road segment is within 300m of a WARNING node: Multiply travel cost by 100x.
        """
        dynamic_graph = self.base_graph.copy()
        avoided_node_ids = set()

        edges_to_remove = []

        for u, v, data in dynamic_graph.edges(data=True):
            u_lat, u_lon = data["u_coord"]
            v_lat, v_lon = data["v_coord"]

            edge_cost = data["base_time_sec"]

            for fnode in flooded_nodes:
                fn_lat = fnode["lat"]
                fn_lon = fnode["lon"]
                fn_level = fnode.get("risk_level", "NORMAL")

                if fn_level in ["WARNING", "CRITICAL"]:
                    dist = distance_point_to_segment_m(fn_lat, fn_lon, u_lat, u_lon, v_lat, v_lon)
                    if dist <= avoidance_radius_m:
                        avoided_node_ids.add(fnode["id"])
                        if fn_level == "CRITICAL":
                            # Road is completely submerged
                            edges_to_remove.append((u, v))
                            break
                        elif fn_level == "WARNING":
                            # Heavy water accumulation - apply 100x penalty
                            edge_cost *= 100.0

            if (u, v) not in edges_to_remove:
                dynamic_graph[u][v]["weight"] = edge_cost

        for u, v in edges_to_remove:
            if dynamic_graph.has_edge(u, v):
                dynamic_graph.remove_edge(u, v)

        return dynamic_graph, list(avoided_node_ids)

    def route_to_nearest_shelter(
        self,
        origin_lat: float,
        origin_lon: float,
        shelters: List[Dict[str, Any]],
        flooded_nodes: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Compute shortest evacuation path from origin to the nearest available shelter,
        avoiding flooded channels.
        """
        if not shelters:
            return None

        # Build dynamic cost graph
        graph, avoided_nodes = self.build_dynamic_graph(flooded_nodes)

        start_node = self.find_nearest_node(origin_lat, origin_lon)
        if not start_node:
            return None

        best_route = None
        best_cost = float("inf")
        target_shelter = None
        best_path_nodes = []

        for shelter in shelters:
            # Check capacity
            rem_capacity = shelter.get("capacity", 100) - shelter.get("current_occupancy", 0)
            if rem_capacity <= 0:
                continue

            shelter_node = self.find_nearest_node(shelter["lat"], shelter["lon"])
            if not shelter_node:
                continue

            try:
                path = nx.shortest_path(graph, source=start_node, target=shelter_node, weight="weight")
                cost = nx.shortest_path_length(graph, source=start_node, target=shelter_node, weight="weight")
                if cost < best_cost:
                    best_cost = cost
                    best_route = path
                    target_shelter = shelter
                    best_path_nodes = path
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue

        # If all routes blocked by critical floodgates, fallback to base graph with heavy warning
        if not best_route:
            logger.warning("No unflooded path found, attempting emergency path on base graph...")
            for shelter in shelters:
                shelter_node = self.find_nearest_node(shelter["lat"], shelter["lon"])
                try:
                    path = nx.shortest_path(self.base_graph, source=start_node, target=shelter_node, weight="base_time_sec")
                    cost = nx.shortest_path_length(self.base_graph, source=start_node, target=shelter_node, weight="base_time_sec")
                    if cost < best_cost:
                        best_cost = cost
                        best_route = path
                        target_shelter = shelter
                        best_path_nodes = path
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    continue

        if not best_route or not target_shelter:
            return None

        # Assemble coordinates list: [origin, node_1, node_2, ..., shelter]
        coordinates = [[origin_lon, origin_lat]]
        total_length_m = haversine_distance_m(
            origin_lat, origin_lon,
            self.base_graph.nodes[best_path_nodes[0]]["lat"],
            self.base_graph.nodes[best_path_nodes[0]]["lon"]
        )

        for i in range(len(best_path_nodes)):
            n_curr = best_path_nodes[i]
            curr_lat = self.base_graph.nodes[n_curr]["lat"]
            curr_lon = self.base_graph.nodes[n_curr]["lon"]
            coordinates.append([curr_lon, curr_lat])

            if i > 0:
                n_prev = best_path_nodes[i - 1]
                edge_data = self.base_graph.get_edge_data(n_prev, n_curr, {})
                total_length_m += edge_data.get("length_m", 0.0)

        # Append final segment to exact shelter coords
        coordinates.append([target_shelter["lon"], target_shelter["lat"]])
        total_length_m += haversine_distance_m(
            coordinates[-2][1], coordinates[-2][0],
            target_shelter["lat"], target_shelter["lon"]
        )

        distance_km = round(total_length_m / 1000.0, 2)
        # Average evacuation transit speed: 25 km/h in urban emergency
        eta_minutes = round(max(2.0, (distance_km / 25.0) * 60.0), 1)

        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates,
            },
            "properties": {
                "distance_km": distance_km,
                "eta_minutes": eta_minutes,
                "target_shelter": target_shelter["name"],
                "avoided_drains": avoided_nodes,
            },
        }

        return {
            "shelter": target_shelter,
            "distance_km": distance_km,
            "eta_minutes": eta_minutes,
            "avoided_flooded_nodes": avoided_nodes,
            "geojson": geojson,
        }


# Global Router Singleton
evacuation_router = EvacuationRouter()
