"use client";

import React, { useEffect, useState } from "react";
import { Area, AreaChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { X, CloudRain, ShieldAlert, Activity, ArrowUpRight, Lock, Unlock } from "lucide-react";
import { NodeData, Reading } from "../../lib/types";
import { fetchNodeReadings } from "../../lib/api";
import { DepthGauge } from "../UI/DepthGauge";

interface NodeDetailDrawerProps {
  node: NodeData | null;
  onClose: () => void;
  onOpenGateControl?: (node: NodeData) => void;
  isOperator?: boolean;
}

export const NodeDetailDrawer: React.FC<NodeDetailDrawerProps> = ({
  node,
  onClose,
  onOpenGateControl,
  isOperator = false,
}) => {
  const [readings, setReadings] = useState<Reading[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!node) return;
    setLoading(true);
    fetchNodeReadings(node.id, 40)
      .then((data) => setReadings(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [node?.id]);

  if (!node) return null;

  const chartData = readings.map((r) => ({
    time: new Date(r.time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    depth: r.depth_cm,
    rain: r.rain_mm_h,
  }));

  const warningLevelCm = node.capacity_cm * 0.70;
  const criticalLevelCm = node.capacity_cm * 0.85;

  return (
    <div className="absolute top-4 right-4 bottom-4 w-96 max-w-[90vw] bg-surface/95 backdrop-blur-md rounded-2xl border border-border shadow-2xl z-[1000] flex flex-col overflow-hidden text-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-border flex items-start justify-between bg-surface-elevated/50">
        <div>
          <div className="flex items-center gap-2">
            <span
              className={`w-3 h-3 rounded-full ${
                node.status === "online" ? "bg-emerald-500 animate-pulse" : "bg-gray-500"
              }`}
            />
            <h2 className="text-lg font-bold text-white tracking-tight">{node.name}</h2>
          </div>
          <p className="text-xs text-gray-400 mt-0.5">
            Ward: <span className="text-gray-200 font-semibold">{node.ward}</span> | ID: {node.id}
          </p>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content Scroll */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Gauge & Key Stats */}
        <div className="grid grid-cols-2 gap-3">
          <DepthGauge
            depthCm={node.latest_depth_cm ?? 0}
            capacityCm={node.capacity_cm}
            riskLevel={node.risk_level}
          />

          <div className="flex flex-col justify-between space-y-2">
            {/* Rain Rate */}
            <div className="p-3 bg-surface-elevated rounded-xl border border-border flex items-center gap-3">
              <CloudRain className="w-6 h-6 text-blue-400 flex-shrink-0" />
              <div>
                <div className="text-xs text-gray-400 uppercase font-semibold">Rainfall</div>
                <div className="text-lg font-bold text-white">
                  {(node.latest_rain_mm_h ?? 0).toFixed(1)}{" "}
                  <span className="text-xs font-normal text-gray-400">mm/h</span>
                </div>
              </div>
            </div>

            {/* Rise Rate */}
            <div className="p-3 bg-surface-elevated rounded-xl border border-border flex items-center gap-3">
              <Activity className="w-6 h-6 text-purple-400 flex-shrink-0" />
              <div>
                <div className="text-xs text-gray-400 uppercase font-semibold">Rise Rate</div>
                <div className="text-lg font-bold text-white">
                  {(node.rise_rate_cm_min ?? 0).toFixed(1)}{" "}
                  <span className="text-xs font-normal text-gray-400">cm/min</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Floodgate Status & Actuation */}
        <div className="p-3 bg-surface-elevated rounded-xl border border-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            {node.current_gate_deg >= 45 ? (
              <Lock className="w-5 h-5 text-amber-400" />
            ) : (
              <Unlock className="w-5 h-5 text-emerald-400" />
            )}
            <div>
              <div className="text-xs text-gray-400 uppercase font-semibold">Floodgate</div>
              <div className="text-sm font-bold text-white">
                {node.current_gate_deg}° {node.current_gate_deg >= 45 ? "(CLOSED)" : "(OPEN)"}
              </div>
            </div>
          </div>

          {isOperator && onOpenGateControl && (
            <button
              onClick={() => onOpenGateControl(node)}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-md transition"
            >
              Control Gate
            </button>
          )}
        </div>

        {/* Historical Sparkline Area Chart */}
        <div className="p-3 bg-surface-elevated rounded-xl border border-border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs uppercase font-semibold text-gray-400 flex items-center gap-1">
              <ArrowUpRight className="w-3.5 h-3.5 text-blue-400" /> Depth Trend (Last 6 Hours)
            </span>
            <span className="text-xs text-gray-500">Threshold: 70% / 85%</span>
          </div>

          <div className="h-44 w-full">
            {loading ? (
              <div className="h-full flex items-center justify-center text-xs text-gray-500">
                Loading telemetry history...
              </div>
            ) : chartData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-xs text-gray-500">
                Awaiting telemetry samples...
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                  <defs>
                    <linearGradient id="depthGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" stroke="#6b7280" fontSize={10} tickLine={false} />
                  <YAxis stroke="#6b7280" fontSize={10} domain={[0, node.capacity_cm * 1.1]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#1f2937", borderColor: "#374151", borderRadius: "8px", fontSize: "11px" }}
                  />
                  <ReferenceLine y={warningLevelCm} stroke="#f97316" strokeDasharray="3 3" label={{ value: "Warning", fill: "#f97316", fontSize: 9 }} />
                  <ReferenceLine y={criticalLevelCm} stroke="#ef4444" strokeDasharray="3 3" label={{ value: "Critical", fill: "#ef4444", fontSize: 9 }} />
                  <Area type="monotone" dataKey="depth" stroke="#3b82f6" fillOpacity={1} fill="url(#depthGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Telemetry metadata footer */}
        <div className="text-[11px] text-gray-500 text-center">
          Mount Height: {node.mount_height_cm} cm | Last Reading:{" "}
          {node.last_seen ? new Date(node.last_seen).toLocaleTimeString() : "Just now"}
        </div>
      </div>
    </div>
  );
};
