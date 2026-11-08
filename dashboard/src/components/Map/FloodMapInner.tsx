"use client";

import React from "react";
import { Circle, MapContainer, Marker, Polyline, Popup, TileLayer, useMapEvents } from "react-leaflet";
import L from "leaflet";
import { EvacuationRouteData, NodeData, RiskLevel, Shelter } from "../../lib/types";

interface FloodMapInnerProps {
  nodes: NodeData[];
  selectedNode: NodeData | null;
  onSelectNode: (node: NodeData) => void;
  evacuationRoute: EvacuationRouteData | null;
  onMapClick?: (lat: number, lon: number) => void;
  shelters?: Shelter[];
}

const DEFAULT_SHELTERS: Shelter[] = [
  { id: "s1", name: "Amberpet Indoor Stadium Camp", lat: 17.3980, lon: 78.5150, capacity: 450, current_occupancy: 42, ward: "Amberpet" },
  { id: "s2", name: "Nimboliadda Community Hall", lat: 17.3820, lon: 78.4950, capacity: 250, current_occupancy: 15, ward: "Malakpet" },
  { id: "s3", name: "Chaderghat Govt High School", lat: 17.3760, lon: 78.4870, capacity: 300, current_occupancy: 20, ward: "Malakpet" },
  { id: "s4", name: "City Model High School & Relief Centre", lat: 17.3680, lon: 78.4680, capacity: 350, current_occupancy: 30, ward: "Charminar" },
];

function createNodeIcon(level: RiskLevel, status: string, name: string) {
  let color = "#10b981"; // Normal
  let isPulsing = false;

  if (status === "offline") {
    color = "#6b7280";
  } else {
    switch (level) {
      case "CRITICAL":
        color = "#ef4444";
        isPulsing = true;
        break;
      case "WARNING":
        color = "#f97316";
        break;
      case "WATCH":
        color = "#f59e0b";
        break;
      default:
        color = "#10b981";
    }
  }

  const html = `
    <div style="position: relative; display: flex; flex-direction: column; align-items: center;">
      <div class="${isPulsing ? 'marker-pulse-critical' : ''}" style="
        width: 28px;
        height: 28px;
        background-color: ${color};
        border: 3px solid #ffffff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.6);
      ">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
        </svg>
      </div>
      <div style="
        background: rgba(17, 24, 39, 0.85);
        color: #f3f4f6;
        font-size: 10px;
        font-weight: 700;
        padding: 2px 6px;
        border-radius: 4px;
        margin-top: 4px;
        white-space: nowrap;
        border: 1px solid #374151;
      ">${name}</div>
    </div>
  `;

  return L.divIcon({
    html,
    className: "custom-node-icon",
    iconSize: [32, 48],
    iconAnchor: [16, 24],
    popupAnchor: [0, -28],
  });
}

function createShelterIcon() {
  const html = `
    <div style="
      width: 26px;
      height: 26px;
      background-color: #3b82f6;
      border: 2px solid #ffffff;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 8px rgba(0,0,0,0.5);
    ">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
        <polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
    </div>
  `;

  return L.divIcon({
    html,
    className: "custom-shelter-icon",
    iconSize: [26, 26],
    iconAnchor: [13, 13],
    popupAnchor: [0, -15],
  });
}

function MapClickHandler({ onMapClick }: { onMapClick?: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      if (onMapClick) {
        onMapClick(e.latlng.lat, e.latlng.lng);
      }
    },
  });
  return null;
}

export const FloodMapInner: React.FC<FloodMapInnerProps> = ({
  nodes,
  selectedNode,
  onSelectNode,
  evacuationRoute,
  onMapClick,
  shelters = DEFAULT_SHELTERS,
}) => {
  // Center on Hyderabad Musi River basin
  const center: [number, number] = [17.3753, 78.4900];

  const routePositions: [number, number][] = evacuationRoute
    ? evacuationRoute.geojson.geometry.coordinates.map((c) => [c[1], c[0]])
    : [];

  return (
    <MapContainer
      center={center}
      zoom={13}
      scrollWheelZoom={true}
      className="w-full h-full"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <MapClickHandler onMapClick={onMapClick} />

      {/* 300m Flooded Avoidance Zones around WARNING & CRITICAL nodes */}
      {nodes.map((node) => {
        if (node.status === "offline") return null;
        if (node.risk_level === "CRITICAL" || node.risk_level === "WARNING") {
          const isCritical = node.risk_level === "CRITICAL";
          return (
            <Circle
              key={`zone-${node.id}`}
              center={[node.lat, node.lon]}
              radius={300}
              pathOptions={{
                color: isCritical ? "#ef4444" : "#f97316",
                fillColor: isCritical ? "#ef4444" : "#f97316",
                fillOpacity: isCritical ? 0.35 : 0.2,
                weight: 2,
                dashArray: isCritical ? "4, 6" : undefined,
              }}
            >
              <Popup>
                <div className="p-1">
                  <div className="text-xs font-bold text-red-400">
                    300m Hazard Zone: {node.name}
                  </div>
                  <div className="text-[11px] text-gray-300">
                    Roads in this zone are heavily penalized or closed.
                  </div>
                </div>
              </Popup>
            </Circle>
          );
        }
        return null;
      })}

      {/* Evacuation Route Polyline */}
      {routePositions.length > 0 && (
        <>
          <Polyline
            positions={routePositions}
            pathOptions={{
              color: "#38bdf8",
              weight: 6,
              opacity: 0.9,
              className: "evacuation-polyline",
            }}
          />
          {/* Outer glow line */}
          <Polyline
            positions={routePositions}
            pathOptions={{
              color: "#0284c7",
              weight: 12,
              opacity: 0.3,
            }}
          />
        </>
      )}

      {/* Shelters Markers */}
      {shelters.map((s) => (
        <Marker
          key={s.id}
          position={[s.lat, s.lon]}
          icon={createShelterIcon()}
        >
          <Popup>
            <div className="p-1.5 space-y-1">
              <div className="text-xs font-bold text-blue-400 flex items-center gap-1">
                <span>🛡️</span> {s.name}
              </div>
              <div className="text-[11px] text-gray-300">
                Ward: {s.ward} | Capacity: {s.capacity} beds
              </div>
              <div className="text-[11px] text-emerald-400 font-semibold">
                Available: {s.capacity - (s.current_occupancy || 0)} slots
              </div>
            </div>
          </Popup>
        </Marker>
      ))}

      {/* Sensor Nodes Markers */}
      {nodes.map((node) => (
        <Marker
          key={node.id}
          position={[node.lat, node.lon]}
          icon={createNodeIcon(node.risk_level, node.status, node.name.split(" ")[0])}
          eventHandlers={{
            click: () => onSelectNode(node),
          }}
        >
          <Popup>
            <div className="p-2 space-y-1 text-xs">
              <div className="font-bold text-white">{node.name}</div>
              <div className="text-gray-400">ID: {node.id} | Ward: {node.ward}</div>
              <div className="flex items-center justify-between pt-1 border-t border-border mt-1">
                <span className="text-gray-300">Water Depth:</span>
                <span className="font-bold text-white">{(node.latest_depth_cm ?? 0).toFixed(1)} cm</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Rainfall:</span>
                <span className="font-bold text-blue-400">{(node.latest_rain_mm_h ?? 0).toFixed(1)} mm/h</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-300">Gate State:</span>
                <span className="font-bold text-amber-400">
                  {node.current_gate_deg}° ({node.current_gate_deg >= 45 ? "CLOSED" : "OPEN"})
                </span>
              </div>
              <button
                onClick={() => onSelectNode(node)}
                className="w-full mt-2 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold text-[11px] transition"
              >
                Inspect Telemetry & Sparkline
              </button>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
};
export default FloodMapInner;
