"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowLeft,
  Bell,
  CheckCircle2,
  Lock,
  Radio,
  RefreshCw,
  ShieldAlert,
  Sliders,
  Unlock,
} from "lucide-react";
import { Alert, EvacuationRouteData, NodeData } from "../../lib/types";
import { fetchAlerts, fetchNodes } from "../../lib/api";
import { useFloodWebSocket } from "../../components/hooks/useFloodWebSocket";
import { FloodMap } from "../../components/Map/FloodMap";
import { NodeDetailDrawer } from "../../components/Sidebar/NodeDetailDrawer";
import { AlertFeed } from "../../components/Sidebar/AlertFeed";
import { GateControlModal } from "../../components/Sidebar/GateControlModal";

export default function OperatorPage() {
  const [nodes, setNodes] = useState<NodeData[]>([]);
  const [selectedNode, setSelectedNode] = useState<NodeData | null>(null);
  const [gateControlNode, setGateControlNode] = useState<NodeData | null>(null);
  const [isGateModalOpen, setIsGateModalOpen] = useState(false);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [evacuationRoute, setEvacuationRoute] = useState<EvacuationRouteData | null>(null);

  const loadData = () => {
    fetchNodes().then(setNodes).catch(console.error);
    fetchAlerts(30).then(setAlerts).catch(console.error);
  };

  useEffect(() => {
    loadData();
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
    },
    onGateActuation: (data) => {
      setNodes((prev) =>
        prev.map((n) => (n.id === data.node_id ? { ...n, current_gate_deg: data.gate_deg } : n))
      );
    },
  });

  const handleOpenGateModal = (node: NodeData) => {
    setGateControlNode(node);
    setIsGateModalOpen(true);
  };

  return (
    <div className="relative w-screen h-screen overflow-hidden flex flex-col bg-background">
      {/* Top Header Navbar */}
      <header className="h-16 px-4 md:px-6 bg-surface/90 backdrop-blur-md border-b border-border z-[1000] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/public"
            className="p-2 rounded-lg bg-surface-elevated hover:bg-gray-800 text-gray-300 transition"
            title="Switch to Public View"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>

          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse" />
              <h1 className="text-sm md:text-base font-bold text-white tracking-tight flex items-center gap-2">
                Operator Ops Command Center
              </h1>
            </div>
            <p className="text-[10px] text-gray-400">Floodgate Actuation & SCADA Telemetry</p>
          </div>

          {/* Connection status */}
          <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-elevated border border-border text-[11px]">
            <span
              className={`w-2 h-2 rounded-full ${
                wsStatus === "connected" ? "bg-emerald-500" : "bg-amber-500"
              }`}
            />
            <span className="text-gray-300 font-medium">WS: {wsStatus}</span>
          </div>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={loadData}
            className="p-2 rounded-lg bg-surface-elevated hover:bg-gray-800 text-gray-300 text-xs font-semibold flex items-center gap-1.5 transition"
            title="Refresh State"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="hidden sm:inline">Refresh</span>
          </button>

          <Link
            href="/public"
            className="px-3 py-1.5 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/40 rounded-xl text-xs font-bold transition"
          >
            Public View
          </Link>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="relative flex-1 w-full h-[calc(100vh-4rem)] flex">
        {/* Left Map View */}
        <div className="relative flex-1 h-full">
          <FloodMap
            nodes={nodes}
            selectedNode={selectedNode}
            onSelectNode={(n) => setSelectedNode(n)}
            evacuationRoute={evacuationRoute}
          />

          {/* Floating Operator Node Table / Quick Controls */}
          <div className="absolute bottom-6 left-6 right-6 md:right-auto md:w-[500px] bg-surface/95 backdrop-blur-md border border-border rounded-2xl p-3.5 shadow-2xl z-[900] text-xs">
            <div className="flex items-center justify-between pb-2 border-b border-border/80 mb-2">
              <span className="font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <Sliders className="w-4 h-4 text-blue-400" /> Storm Drain Floodgates
              </span>
              <span className="text-gray-400 text-[11px]">{nodes.length} Nodes Configured</span>
            </div>

            <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
              {nodes.map((node) => (
                <div
                  key={node.id}
                  className="flex items-center justify-between p-2 bg-surface-elevated/70 hover:bg-surface-elevated rounded-xl border border-border/60 transition"
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={`w-2.5 h-2.5 rounded-full ${
                        node.risk_level === "CRITICAL"
                          ? "bg-red-500 animate-pulse"
                          : node.risk_level === "WARNING"
                          ? "bg-orange-500"
                          : node.risk_level === "WATCH"
                          ? "bg-amber-500"
                          : "bg-emerald-500"
                      }`}
                    />
                    <div>
                      <div className="font-semibold text-white text-xs">{node.name}</div>
                      <div className="text-[10px] text-gray-400">
                        {node.id} | Depth: {(node.latest_depth_cm ?? 0).toFixed(1)}/{node.capacity_cm}cm
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                        node.current_gate_deg >= 45
                          ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                          : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                      }`}
                    >
                      {node.current_gate_deg}° {node.current_gate_deg >= 45 ? "CLOSED" : "OPEN"}
                    </span>

                    <button
                      onClick={() => handleOpenGateModal(node)}
                      className="px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-[11px] font-semibold transition"
                    >
                      Override
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Floating Alert Feed Drawer */}
        <div className="hidden lg:block absolute top-4 right-4 w-96 z-[950]">
          <AlertFeed
            alerts={alerts}
            onSelectNode={(nodeId) => {
              const match = nodes.find((n) => n.id === nodeId);
              if (match) setSelectedNode(match);
            }}
          />
        </div>

        {/* Selected Node Details Drawer */}
        <NodeDetailDrawer
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
          onOpenGateControl={handleOpenGateModal}
          isOperator={true}
        />

        {/* Operator Actuation Confirmation Modal */}
        <GateControlModal
          node={gateControlNode}
          isOpen={isGateModalOpen}
          onClose={() => setIsGateModalOpen(false)}
          onSuccess={loadData}
        />
      </main>
    </div>
  );
}
