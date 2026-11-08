"use client";

import React, { useState } from "react";
import { AlertOctagon, Check, Lock, Unlock, X } from "lucide-react";
import { NodeData } from "../../lib/types";
import { postGateOverride } from "../../lib/api";

interface GateControlModalProps {
  node: NodeData | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const GateControlModal: React.FC<GateControlModalProps> = ({
  node,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [targetAngle, setTargetAngle] = useState<number>(90);
  const [reason, setReason] = useState<string>("Manual operator safety override");
  const [apiKey, setApiKey] = useState<string>("dev-operator-key-42");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !node) return null;

  const handleActuate = async () => {
    setLoading(true);
    setError(null);
    try {
      await postGateOverride(node.id, targetAngle, reason, apiKey);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to dispatch actuation command.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[2000] bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-surface border border-border w-full max-w-md rounded-2xl shadow-2xl p-6 text-gray-200">
        <div className="flex items-center justify-between pb-3 border-b border-border">
          <div className="flex items-center gap-2">
            <AlertOctagon className="w-5 h-5 text-amber-400" />
            <h3 className="text-base font-bold text-white">Operator Floodgate Control</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mt-4 space-y-4">
          <div className="p-3 bg-surface-elevated rounded-xl border border-border text-xs space-y-1">
            <div>
              Target Drain Node: <span className="font-bold text-white">{node.name}</span> ({node.id})
            </div>
            <div>
              Current Gate Status:{" "}
              <span className="font-bold text-white">{node.current_gate_deg}°</span> (
              {node.current_gate_deg >= 45 ? "CLOSED" : "OPEN"})
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">
              Select Desired Action
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setTargetAngle(90)}
                className={`p-3 rounded-xl border flex flex-col items-center gap-1.5 transition ${
                  targetAngle === 90
                    ? "bg-red-500/20 border-red-500 text-white font-bold"
                    : "bg-surface-elevated border-border text-gray-400 hover:text-white"
                }`}
              >
                <Lock className="w-5 h-5 text-red-400" />
                <span>Close Gate (90°)</span>
                <span className="text-[10px] text-gray-400">Block Sewer Backflow</span>
              </button>

              <button
                type="button"
                onClick={() => setTargetAngle(0)}
                className={`p-3 rounded-xl border flex flex-col items-center gap-1.5 transition ${
                  targetAngle === 0
                    ? "bg-emerald-500/20 border-emerald-500 text-white font-bold"
                    : "bg-surface-elevated border-border text-gray-400 hover:text-white"
                }`}
              >
                <Unlock className="w-5 h-5 text-emerald-400" />
                <span>Open Gate (0°)</span>
                <span className="text-[10px] text-gray-400">Normal Gravity Discharge</span>
              </button>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">
              Reason / Audit Note
            </label>
            <input
              type="text"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full bg-surface-elevated border border-border rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-1.5">
              Operator API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full bg-surface-elevated border border-border rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            />
          </div>

          {error && <div className="text-xs text-red-400 bg-red-500/10 p-2.5 rounded-lg border border-red-500/30">{error}</div>}

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-surface-elevated hover:bg-gray-800 text-gray-300 rounded-xl text-sm font-semibold transition"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleActuate}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-xl text-sm font-bold shadow-lg transition flex items-center justify-center gap-2"
            >
              {loading ? "Actuating..." : "Confirm & Dispatch"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
