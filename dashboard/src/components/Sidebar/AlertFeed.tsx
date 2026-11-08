"use client";

import React from "react";
import { AlertCircle, AlertTriangle, Bell, Clock, ShieldAlert } from "lucide-react";
import { Alert, RiskLevel } from "../../lib/types";

interface AlertFeedProps {
  alerts: Alert[];
  onSelectNode?: (nodeId: string) => void;
}

export const AlertFeed: React.FC<AlertFeedProps> = ({ alerts, onSelectNode }) => {
  const getBadgeStyle = (level: RiskLevel) => {
    switch (level) {
      case "CRITICAL":
        return "bg-red-500/20 text-red-400 border-red-500/40";
      case "WARNING":
        return "bg-orange-500/20 text-orange-400 border-orange-500/40";
      case "WATCH":
        return "bg-amber-500/20 text-amber-400 border-amber-500/40";
      default:
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/40";
    }
  };

  const getIcon = (level: RiskLevel) => {
    switch (level) {
      case "CRITICAL":
        return <ShieldAlert className="w-4 h-4 text-red-400 flex-shrink-0" />;
      case "WARNING":
        return <AlertTriangle className="w-4 h-4 text-orange-400 flex-shrink-0" />;
      default:
        return <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0" />;
    }
  };

  return (
    <div className="bg-surface/95 backdrop-blur-md rounded-2xl border border-border p-4 shadow-xl flex flex-col max-h-[380px] overflow-hidden">
      <div className="flex items-center justify-between pb-3 border-b border-border">
        <div className="flex items-center gap-2">
          <Bell className="w-4 h-4 text-blue-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Early Warning Alerts</h3>
        </div>
        <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full font-semibold">
          {alerts.length} Dispatched
        </span>
      </div>

      <div className="flex-1 overflow-y-auto mt-3 space-y-2.5 pr-1">
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-xs text-gray-500">
            No active emergency alerts. All monitored storm drains within safe parameters.
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              onClick={() => onSelectNode && onSelectNode(alert.node_id)}
              className="p-3 bg-surface-elevated/70 hover:bg-surface-elevated rounded-xl border border-border/80 transition cursor-pointer space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  {getIcon(alert.level)}
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getBadgeStyle(
                      alert.level
                    )}`}
                  >
                    {alert.level}
                  </span>
                  <span className="text-xs font-semibold text-gray-300">[{alert.node_id}]</span>
                </div>
                <div className="flex items-center gap-1 text-[11px] text-gray-400">
                  <Clock className="w-3 h-3" />
                  {new Date(alert.sent_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </div>
              </div>

              <p className="text-xs text-gray-300 leading-snug">{alert.message}</p>

              <div className="text-[10px] text-gray-500 flex items-center justify-between pt-1 border-t border-border/40">
                <span>Channel: {alert.channel.toUpperCase()} (SMS/WA)</span>
                <span>Recipients: {alert.recipients_count} citizens</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
