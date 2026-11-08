export type RiskLevel = "NORMAL" | "WATCH" | "WARNING" | "CRITICAL";

export interface NodeData {
  id: string;
  name: string;
  lat: float;
  lon: float;
  ward: string;
  mount_height_cm: number;
  capacity_cm: number;
  status: "online" | "offline" | string;
  last_seen?: string;
  current_gate_deg: number;
  latest_depth_cm?: number;
  latest_rain_mm_h?: number;
  latest_ratio?: number;
  rise_rate_cm_min?: number;
  risk_level: RiskLevel;
}

export interface Reading {
  time: string;
  node_id: string;
  depth_cm: number;
  rain_mm_h: number;
  gate_deg: number;
  rssi: number;
}

export interface Alert {
  id: number;
  node_id: string;
  level: RiskLevel;
  message: string;
  channel: string;
  sent_at: string;
  recipients_count: number;
}

export interface Shelter {
  id: string;
  name: string;
  lat: number;
  lon: number;
  capacity: number;
  current_occupancy: number;
  ward: string;
  contact_phone?: string;
}

export interface EvacuationRouteData {
  shelter: Shelter;
  distance_km: number;
  eta_minutes: number;
  avoided_flooded_nodes: string[];
  geojson: {
    type: "Feature";
    geometry: {
      type: "LineString";
      coordinates: [number, number][]; // [lon, lat]
    };
    properties: {
      distance_km: number;
      eta_minutes: number;
      target_shelter: string;
      avoided_drains: string[];
    };
  };
}

export interface LiveTelemetryMsg {
  node_id: string;
  name: string;
  ward: string;
  time: string;
  depth_cm: number;
  capacity_cm: number;
  ratio: number;
  rain_mm_h: number;
  gate_deg: number;
  rssi: number;
  rise_rate_cm_min: number;
  risk_level: RiskLevel;
}
