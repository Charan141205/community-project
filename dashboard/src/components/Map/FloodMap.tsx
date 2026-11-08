"use client";

import dynamic from "next/dynamic";
import React from "react";
import { EvacuationRouteData, NodeData, Shelter } from "../../lib/types";

const DynamicMap = dynamic(() => import("./FloodMapInner"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex flex-col items-center justify-center bg-surface text-gray-400">
      <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-3" />
      <span className="text-sm font-medium">Loading Hyderabad GIS Drainage Map...</span>
    </div>
  ),
});

interface FloodMapProps {
  nodes: NodeData[];
  selectedNode: NodeData | null;
  onSelectNode: (node: NodeData) => void;
  evacuationRoute: EvacuationRouteData | null;
  onMapClick?: (lat: number, lon: number) => void;
  shelters?: Shelter[];
}

export const FloodMap: React.FC<FloodMapProps> = (props) => {
  return <DynamicMap {...props} />;
};
