"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { Alert, LiveTelemetryMsg, NodeData } from "../../lib/types";

export type ConnectionStatus = "connected" | "reconnecting" | "disconnected";

interface UseFloodWebSocketProps {
  onTelemetry?: (msg: LiveTelemetryMsg) => void;
  onAlert?: (alert: Alert) => void;
  onGateActuation?: (data: { node_id: string; gate_deg: number; reason: string; triggered_by: string }) => void;
  onNodeStatus?: (data: { node_id: string; status: string; timestamp: string }) => void;
}

export function useFloodWebSocket({
  onTelemetry,
  onAlert,
  onGateActuation,
  onNodeStatus,
}: UseFloodWebSocketProps = {}) {
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const backoffRef = useRef(1000);

  const connect = useCallback(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/live";

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus("connected");
        backoffRef.current = 1000;
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "telemetry" && onTelemetry) {
            onTelemetry(msg.data);
          } else if (msg.type === "alert" && onAlert) {
            onAlert(msg.data);
          } else if (msg.type === "gate_actuation" && onGateActuation) {
            onGateActuation(msg.data);
          } else if (msg.type === "node_status" && onNodeStatus) {
            onNodeStatus(msg.data);
          }
        } catch (e) {
          console.error("Error parsing WebSocket message:", e);
        }
      };

      ws.onclose = () => {
        setStatus("reconnecting");
        const nextDelay = Math.min(backoffRef.current * 1.5, 15000);
        backoffRef.current = nextDelay;
        reconnectTimeoutRef.current = setTimeout(connect, nextDelay);
      };

      ws.onerror = (err) => {
        ws.close();
      };
    } catch (err) {
      setStatus("disconnected");
      reconnectTimeoutRef.current = setTimeout(connect, 3000);
    }
  }, [onTelemetry, onAlert, onGateActuation, onNodeStatus]);

  useEffect(() => {
    connect();

    // Ping interval to keep connection alive
    const pingInterval = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send("ping");
      }
    }, 20000);

    return () => {
      clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { status };
}
