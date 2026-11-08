"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  Bell,
  CheckCircle2,
  ChevronRight,
  Info,
  MapPin,
  Navigation,
  Radio,
  ShieldAlert,
  ShieldCheck,
  X,
} from "lucide-react";
import { Alert, EvacuationRouteData, NodeData } from "../../lib/types";
import { fetchAlerts, fetchEvacuation, fetchNodes } from "../../lib/api";
import { useFloodWebSocket } from "../../components/hooks/useFloodWebSocket";
import { FloodMap } from "../../components/Map/FloodMap";
import { NodeDetailDrawer } from "../../components/Sidebar/NodeDetailDrawer";
import { SubscribeModal } from "../../components/UI/SubscribeModal";

export default function PublicPage() {
  const [nodes, setNodes] = useState<NodeData[]>([]);
  const [selectedNode, setSelectedNode] = useState<NodeData | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [evacuationRoute, setEvacuationRoute] = useState<EvacuationRouteData | null>(null);
  const [isSubscribeOpen, setIsSubscribeOpen] = useState(false);
  const [activeToast, setActiveToast] = useState<Alert | null>(null);
  const [evacLoading, setEvacLoading] = useState(false);

  // Initial load
  useEffect(() => {
    fetchNodes().then(setNodes).catch(console.error);
    fetchAlerts(10).then(setAlerts).catch(console.error);
  }, []);

  // WebSocket Live Sync
  const { status: wsStatus } = useFloodWebSocket({
    onTelemetry: (msg) => {
      setNodes((prev) =>
        prev.map((n) =>
          n.id === msg.node_id
            ? {
                ...n,
                status: "online",
                latest_depth_cm: msg.depth_cm,
                latest_rain_mm_h: msg.rain_mm_h,
                latest_ratio: msg.ratio,
                rise_rate_cm_min: msg.rise_rate_cm_min,
                risk_level: msg.risk_level,
                current_gate_deg: msg.gate_deg,
                last_seen: msg.time,
              }
            : n
        )
      );

      // Update selected node if currently open
      if (selectedNode && selectedNode.id === msg.node_id) {
        setSelectedNode((prev) =>
          prev
            ? {
                ...prev,
                latest_depth_cm: msg.depth_cm,
                latest_rain_mm_h: msg.rain_mm_h,
                latest_ratio: msg.ratio,
                rise_rate_cm_min: msg.rise_rate_cm_min,
                risk_level: msg.risk_level,
                current_gate_deg: msg.gate_deg,
                last_seen: msg.time,
              }
            : null
        );
      }
    },
    onAlert: (newAlert) => {
      setAlerts((prev) => [newAlert, ...prev]);
      setActiveToast(newAlert);
      setTimeout(() => setActiveToast(null), 8000);
    },
    onGateActuation: (data) => {
      setNodes((prev) =>
        prev.map((n) => (n.id === data.node_id ? { ...n, current_gate_deg: data.gate_deg } : n))
      );
    },
  });

  const handleMapClick = async (lat: number, lon: number) => {
    setEvacLoading(true);
    try {
      const route = await fetchEvacuation(lat, lon);
      setEvacuationRoute(route);
    } catch (e) {
      console.error("Evacuation calculation error:", e);
    } finally {
      setEvacLoading(false);
    }
  };

  const criticalCount = nodes.filter((n) => n.risk_level === "CRITICAL").length;
  const warningCount = nodes.filter((n) => n.risk_level === "WARNING").length;

  return (
    <div className="relative w-screen h-screen overflow-hidden flex flex-col bg-background">
      {/* Top Header Navbar */}
      <header className="h-16 px-4 md:px-6 bg-surface/90 backdrop-blur-md border-b border-border z-[1000] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-sm md:text-base font-bold text-white tracking-tight flex items-center gap-2">
                flood-ews <span className="text-xs font-normal text-gray-400">| Community Portal</span>
              </h1>
              <p className="text-[10px] text-gray-400">Musi River Basin & Urban Stormwater Watch</p>
            </div>
          </Link>

          {/* Live WS Status Pill */}
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-elevated border border-border text-[11px]">
            <span
              className={`w-2 h-2 rounded-full ${
                wsStatus === "connected" ? "bg-emerald-500 animate-pulse" : "bg-amber-500"
              }`}
            />
            <span className="text-gray-300 font-medium">
              {wsStatus === "connected" ? "Live Telemetry" : "Reconnecting..."}
            </span>
          </div>
        </div>

        {/* Hazard Quick Summary */}
        <div className="hidden lg:flex items-center gap-3 text-xs">
          {criticalCount > 0 && (
            <div className="flex items-center gap-1.5 px-3 py-1 bg-red-500/20 border border-red-500/40 text-red-400 rounded-full font-bold animate-pulse">
              <ShieldAlert className="w-4 h-4" />
              <span>{criticalCount} Critical Inundation</span>
            </div>
          )}
          {warningCount > 0 && (
            <div className="flex items-center gap-1.5 px-3 py-1 bg-orange-500/20 border border-orange-500/40 text-orange-400 rounded-full font-bold">
              <AlertTriangle className="w-4 h-4" />
              <span>{warningCount} High Water Warning</span>
            </div>
          )}
          {criticalCount === 0 && warningCount === 0 && (
            <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 rounded-full font-semibold">
              <CheckCircle2 className="w-4 h-4" />
              <span>Drainage Channels Normal</span>
            </div>
          )}
        </div>

        {/* Right CTA Buttons */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setIsSubscribeOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md transition"
          >
            <Bell className="w-4 h-4" />
            <span className="hidden sm:inline">Get SMS / WhatsApp Alerts</span>
            <span className="sm:hidden">Alerts</span>
          </button>

          <Link
            href="/ops"
            className="flex items-center gap-1 px-3 py-1.5 bg-surface-elevated hover:bg-gray-800 border border-border text-gray-300 rounded-xl text-xs font-semibold transition"
          >
            <Radio className="w-4 h-4 text-amber-400" />
            <span className="hidden md:inline">Operator Ops</span>
          </Link>
        </div>
      </header>

      {/* Main Interactive Map Area */}
      <main className="relative flex-1 w-full h-[calc(100vh-4rem)]">
        <FloodMap
          nodes={nodes}
          selectedNode={selectedNode}
          onSelectNode={(n) => setSelectedNode(n)}
          evacuationRoute={evacuationRoute}
          onMapClick={handleMapClick}
        />

        {/* Evacuation Route Info Bar (Floating at top) */}
        {evacuationRoute && (
          <div className="absolute top-4 left-4 right-4 md:left-1/2 md:-translate-x-1/2 md:max-w-2xl bg-surface/95 backdrop-blur-md border border-blue-500/40 rounded-2xl p-4 shadow-2xl z-[1000] text-gray-200 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 animate-in fade-in slide-in-from-top-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-500/20 text-blue-400 flex items-center justify-center flex-shrink-0">
                <Navigation className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <div className="text-xs text-blue-400 font-bold uppercase tracking-wider flex items-center gap-1">
                  <span>Safe Evacuation Route Computed</span>
                </div>
                <div className="text-sm font-bold text-white">
                  Target: {evacuationRoute.shelter.name}
                </div>
                <div className="text-xs text-gray-400">
                  Distance: <span className="text-white font-semibold">{evacuationRoute.distance_km} km</span> | ETA:{" "}
                  <span className="text-emerald-400 font-semibold">{evacuationRoute.eta_minutes} mins</span>
                  {evacuationRoute.avoided_flooded_nodes.length > 0 && (
                    <span className="text-amber-400 font-medium">
                      {" "}
                      (Rerouted to avoid {evacuationRoute.avoided_flooded_nodes.length} submerged drains)
                    </span>
                  )}
                </div>
              </div>
            </div>

            <button
              onClick={() => setEvacuationRoute(null)}
              className="p-1 rounded-lg text-gray-400 hover:text-white self-end md:self-center"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Helpful Click-to-Route Guidance Pill */}
        {!evacuationRoute && (
          <div className="absolute top-4 left-4 bg-surface/90 backdrop-blur-md border border-border px-3 py-1.5 rounded-full shadow-lg z-[990] text-xs text-gray-300 flex items-center gap-2 pointer-events-none">
            <MapPin className="w-4 h-4 text-blue-400" />
            <span>Click anywhere on the map to find nearest safe shelter & route</span>
          </div>
        )}

        {/* Selected Node Details Drawer */}
        <NodeDetailDrawer
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
          isOperator={false}
        />

        {/* Live Escalation Alert Toast */}
        {activeToast && (
          <div className="absolute bottom-6 left-6 max-w-md bg-red-950/95 border border-red-500/50 rounded-2xl p-4 shadow-2xl z-[1500] text-white flex items-start gap-3 animate-in fade-in slide-in-from-bottom-5">
            <ShieldAlert className="w-6 h-6 text-red-400 flex-shrink-0 animate-bounce" />
            <div className="flex-1 text-xs space-y-1">
              <div className="font-bold uppercase tracking-wider text-red-300">
                Emergency Alert [{activeToast.level}]
              </div>
              <p className="text-gray-200">{activeToast.message}</p>
            </div>
            <button
              onClick={() => setActiveToast(null)}
              className="p-1 rounded-lg text-gray-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
      </main>

      {/* Citizen Opt-in Modal */}
      <SubscribeModal
        isOpen={isSubscribeOpen}
        onClose={() => setIsSubscribeOpen(false)}
      />
    </div>
  );
}
