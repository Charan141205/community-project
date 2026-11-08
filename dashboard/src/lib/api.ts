import { Alert, EvacuationRouteData, NodeData, Reading } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchNodes(): Promise<NodeData[]> {
  const res = await fetch(`${API_BASE}/api/nodes`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch nodes");
  return res.json();
}

export async function fetchNodeReadings(nodeId: string, limit: number = 60): Promise<Reading[]> {
  const res = await fetch(`${API_BASE}/api/nodes/${nodeId}/readings?limit=${limit}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch readings for ${nodeId}`);
  return res.json();
}

export async function fetchAlerts(limit: number = 20): Promise<Alert[]> {
  const res = await fetch(`${API_BASE}/api/alerts?limit=${limit}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch alerts");
  return res.json();
}

export async function fetchEvacuation(lat: number, lon: number): Promise<EvacuationRouteData> {
  const res = await fetch(`${API_BASE}/api/evacuation?lat=${lat}&lon=${lon}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to compute evacuation route");
  return res.json();
}

export async function postGateOverride(
  nodeId: string,
  gateAngle: number,
  reason: string,
  apiKey: string = "dev-operator-key-42"
): Promise<any> {
  const res = await fetch(`${API_BASE}/api/nodes/${nodeId}/gate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKey,
    },
    body: JSON.stringify({ gate_angle: gateAngle, reason }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to actuate floodgate");
  }
  return res.json();
}

export async function registerSubscriber(data: {
  phone: string;
  name: string;
  ward: string;
  language: "en" | "te" | "hi";
}): Promise<any> {
  const res = await fetch(`${API_BASE}/api/subscribers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to register subscriber");
  return res.json();
}
