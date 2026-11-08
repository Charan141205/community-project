"use client";

import React from "react";
import { RiskLevel } from "../../lib/types";

interface DepthGaugeProps {
  depthCm: number;
  capacityCm: number;
  riskLevel: RiskLevel;
}

export const DepthGauge: React.FC<DepthGaugeProps> = ({ depthCm, capacityCm, riskLevel }) => {
  const ratio = capacityCm > 0 ? Math.min(Math.max(depthCm / capacityCm, 0), 1) : 0;
  const percentage = Math.round(ratio * 100);

  const getColor = (level: RiskLevel) => {
    switch (level) {
      case "CRITICAL":
        return "#ef4444";
      case "WARNING":
        return "#f97316";
      case "WATCH":
        return "#f59e0b";
      default:
        return "#10b981";
    }
  };

  const color = getColor(riskLevel);

  return (
    <div className="flex flex-col items-center p-3 bg-surface-elevated rounded-xl border border-border">
      <div className="relative w-32 h-32 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Background Track */}
          <circle
            cx="50"
            cy="50"
            r="40"
            stroke="#1f2937"
            strokeWidth="10"
            fill="transparent"
          />
          {/* Fill Bar */}
          <circle
            cx="50"
            cy="50"
            r="40"
            stroke={color}
            strokeWidth="10"
            strokeDasharray={251.2}
            strokeDashoffset={251.2 - 251.2 * ratio}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-700 ease-out"
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className="text-2xl font-bold tracking-tight text-white">{percentage}%</span>
          <span className="text-xs uppercase tracking-wider font-semibold text-gray-400">Filled</span>
        </div>
      </div>
      <div className="mt-2 text-center">
        <div className="text-sm font-medium text-gray-200">
          <span className="text-white font-bold">{depthCm.toFixed(1)} cm</span> / {capacityCm} cm
        </div>
        <div
          className="mt-1 text-xs px-2.5 py-0.5 rounded-full font-bold uppercase inline-block"
          style={{ backgroundColor: `${color}20`, color: color }}
        >
          {riskLevel}
        </div>
      </div>
    </div>
  );
};
