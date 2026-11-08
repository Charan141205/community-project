"""
Risk Assessment Engine for flood-ews.
Pure functional risk evaluations, rise-rate tracking, and hysteresis state management.
"""

from collections import deque
from enum import IntEnum
from typing import Deque, Dict, List, Optional, Tuple


class RiskLevel(IntEnum):
    NORMAL = 0
    WATCH = 1
    WARNING = 2
    CRITICAL = 3

    @property
    def label(self) -> str:
        return self.name


def calculate_ratio(depth_cm: float, capacity_cm: float) -> float:
    """Calculate fill ratio of channel (0.0 to 1.0+)."""
    if capacity_cm <= 0.0:
        return 0.0
    return max(0.0, depth_cm / capacity_cm)


def compute_rise_rate(history: List[Tuple[float, float]], current_ts: float, current_depth: float, window_seconds: float = 180.0) -> float:
    """
    Compute rate of rise in cm/min over the past `window_seconds` (default 3 minutes).
    `history` is a list of (timestamp_seconds, depth_cm).
    """
    if not history:
        return 0.0

    target_ts = current_ts - window_seconds
    baseline_depth: Optional[float] = None
    baseline_ts: Optional[float] = None

    # Find earliest reading within or closest to the 3-minute window
    for ts, depth in history:
        if ts <= target_ts:
            baseline_ts = ts
            baseline_depth = depth
        else:
            if baseline_depth is None:
                baseline_ts = ts
                baseline_depth = depth
            break

    if baseline_ts is None or baseline_depth is None:
        return 0.0

    dt_minutes = (current_ts - baseline_ts) / 60.0
    if dt_minutes < 0.2:  # Less than 12 seconds elapsed, avoid division instability
        return 0.0

    rate = (current_depth - baseline_depth) / dt_minutes
    return round(rate, 2)


def evaluate_raw_risk(ratio: float, rate_cm_min: float, rain_mm_h: float) -> RiskLevel:
    """
    Evaluate instantaneous flood risk level without hysteresis.

    Thresholds:
    - CRITICAL: ratio >= 85%
    - WARNING:  70% <= ratio < 85% OR (rain > 30 mm/h and rising rate > 0)
    - WATCH:    50% <= ratio < 70% OR rate > 5 cm/min
    - NORMAL:   ratio < 50%
    """
    if ratio >= 0.85:
        return RiskLevel.CRITICAL

    if ratio >= 0.70 or (rain_mm_h > 30.0 and rate_cm_min > 0.0):
        return RiskLevel.WARNING

    if ratio >= 0.50 or rate_cm_min > 5.0:
        return RiskLevel.WATCH

    return RiskLevel.NORMAL


class NodeRiskTracker:
    """
    Tracks stateful telemetry history and applies asymmetric hysteresis per node:
    - Immediate escalation on elevated risk.
    - Requires 3 consecutive lower readings before de-escalating.
    """

    def __init__(self, node_id: str, capacity_cm: float):
        self.node_id = node_id
        self.capacity_cm = capacity_cm
        self.current_level = RiskLevel.NORMAL
        # Store recent readings: (timestamp_sec, depth_cm)
        self.history: Deque[Tuple[float, float]] = deque(maxlen=60)
        # Hysteresis de-escalation tracking
        self.lower_reading_count = 0
        self.pending_lower_level: Optional[RiskLevel] = None

    def update(
        self,
        timestamp: float,
        depth_cm: float,
        rain_mm_h: float,
    ) -> Tuple[RiskLevel, float, float, bool]:
        """
        Process a new reading for this node.
        Returns:
            (effective_risk_level, ratio, rise_rate_cm_min, did_escalate)
        """
        ratio = calculate_ratio(depth_cm, self.capacity_cm)
        rate_cm_min = compute_rise_rate(list(self.history), timestamp, depth_cm, window_seconds=180.0)

        # Append to time-series history
        self.history.append((timestamp, depth_cm))

        # Evaluate raw instantaneous level
        raw_level = evaluate_raw_risk(ratio, rate_cm_min, rain_mm_h)

        previous_level = self.current_level
        did_escalate = False

        if raw_level > self.current_level:
            # Immediate escalation
            self.current_level = raw_level
            self.lower_reading_count = 0
            self.pending_lower_level = None
            did_escalate = True
        elif raw_level < self.current_level:
            # Hysteresis: requires 3 consecutive lower readings to de-escalate
            if self.pending_lower_level == raw_level:
                self.lower_reading_count += 1
            else:
                self.pending_lower_level = raw_level
                self.lower_reading_count = 1

            if self.lower_reading_count >= 3:
                self.current_level = raw_level
                self.lower_reading_count = 0
                self.pending_lower_level = None
        else:
            # Same level, reset de-escalation counter
            self.lower_reading_count = 0
            self.pending_lower_level = None

        return self.current_level, ratio, rate_cm_min, did_escalate
