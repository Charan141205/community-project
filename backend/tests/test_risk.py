"""
Unit tests for the Risk Engine:
Ratio calculations, 3-minute rise rate, threshold boundary conditions, and asymmetric hysteresis.
"""

import pytest
from backend.app.risk import (
    RiskLevel,
    calculate_ratio,
    compute_rise_rate,
    evaluate_raw_risk,
    NodeRiskTracker,
)


def test_calculate_ratio():
    assert calculate_ratio(90.0, 180.0) == 0.50
    assert calculate_ratio(180.0, 180.0) == 1.00
    assert calculate_ratio(0.0, 180.0) == 0.00
    assert calculate_ratio(10.0, 0.0) == 0.00  # Avoid zero division


def test_compute_rise_rate():
    # 3 readings over 3 minutes: (0s, 30cm), (60s, 36cm), (180s, 48cm)
    history = [
        (1000.0, 30.0),
        (1060.0, 36.0),
    ]
    # Current reading at 1180s (3 min later) with depth 48cm
    # Rise = 48 - 30 = 18cm over 3 minutes -> 6.0 cm/min
    rate = compute_rise_rate(history, current_ts=1180.0, current_depth=48.0, window_seconds=180.0)
    assert rate == 6.0


def test_evaluate_raw_risk_thresholds():
    # NORMAL: ratio < 50%, rate <= 5
    assert evaluate_raw_risk(ratio=0.45, rate_cm_min=2.0, rain_mm_h=10.0) == RiskLevel.NORMAL

    # WATCH: 50% <= ratio < 70%
    assert evaluate_raw_risk(ratio=0.55, rate_cm_min=1.0, rain_mm_h=10.0) == RiskLevel.WATCH

    # WATCH: ratio < 50% but rapid rise rate > 5 cm/min
    assert evaluate_raw_risk(ratio=0.35, rate_cm_min=6.2, rain_mm_h=10.0) == RiskLevel.WATCH

    # WARNING: 70% <= ratio < 85%
    assert evaluate_raw_risk(ratio=0.75, rate_cm_min=1.0, rain_mm_h=15.0) == RiskLevel.WARNING

    # WARNING: ratio < 70% but heavy rain > 30 mm/h and rising
    assert evaluate_raw_risk(ratio=0.40, rate_cm_min=2.5, rain_mm_h=35.0) == RiskLevel.WARNING

    # CRITICAL: ratio >= 85%
    assert evaluate_raw_risk(ratio=0.86, rate_cm_min=0.5, rain_mm_h=10.0) == RiskLevel.CRITICAL
    assert evaluate_raw_risk(ratio=0.95, rate_cm_min=0.0, rain_mm_h=0.0) == RiskLevel.CRITICAL


def test_hysteresis_immediate_escalation():
    """Verify that any escalation happens on the very first reading."""
    tracker = NodeRiskTracker(node_id="test-drain", capacity_cm=100.0)
    assert tracker.current_level == RiskLevel.NORMAL

    # Immediate jump to WARNING (depth 75cm -> ratio 0.75)
    level, ratio, rate, did_escalate = tracker.update(timestamp=100.0, depth_cm=75.0, rain_mm_h=10.0)
    assert level == RiskLevel.WARNING
    assert did_escalate is True

    # Immediate escalation to CRITICAL (depth 88cm -> ratio 0.88)
    level, ratio, rate, did_escalate = tracker.update(timestamp=110.0, depth_cm=88.0, rain_mm_h=10.0)
    assert level == RiskLevel.CRITICAL
    assert did_escalate is True


def test_hysteresis_three_tick_deescalation():
    """Verify that de-escalation requires exactly 3 consecutive lower readings."""
    tracker = NodeRiskTracker(node_id="test-drain", capacity_cm=100.0)

    # Escalate to CRITICAL
    tracker.update(timestamp=100.0, depth_cm=90.0, rain_mm_h=5.0)
    assert tracker.current_level == RiskLevel.CRITICAL

    # 1st lower reading (depth drops to 60cm -> WATCH level)
    level, _, _, did_escalate = tracker.update(timestamp=110.0, depth_cm=60.0, rain_mm_h=5.0)
    assert level == RiskLevel.CRITICAL  # Still CRITICAL due to hysteresis
    assert did_escalate is False

    # 2nd consecutive lower reading
    level, _, _, _ = tracker.update(timestamp=120.0, depth_cm=58.0, rain_mm_h=5.0)
    assert level == RiskLevel.CRITICAL  # Still CRITICAL

    # 3rd consecutive lower reading -> NOW de-escalates to WATCH!
    level, _, _, _ = tracker.update(timestamp=130.0, depth_cm=55.0, rain_mm_h=5.0)
    assert level == RiskLevel.WATCH


def test_hysteresis_counter_reset_on_spike():
    """Verify that a sudden spike resets the de-escalation counter."""
    tracker = NodeRiskTracker(node_id="test-drain", capacity_cm=100.0)
    tracker.update(timestamp=100.0, depth_cm=90.0, rain_mm_h=5.0)
    assert tracker.current_level == RiskLevel.CRITICAL

    # 1st lower reading
    tracker.update(timestamp=110.0, depth_cm=60.0, rain_mm_h=5.0)
    assert tracker.current_level == RiskLevel.CRITICAL

    # 2nd lower reading
    tracker.update(timestamp=120.0, depth_cm=60.0, rain_mm_h=5.0)
    assert tracker.current_level == RiskLevel.CRITICAL

    # Wave surge back to CRITICAL
    tracker.update(timestamp=130.0, depth_cm=89.0, rain_mm_h=5.0)
    assert tracker.current_level == RiskLevel.CRITICAL
    assert tracker.lower_reading_count == 0  # Counter reset

    # Subsequent lower reading starts count over at 1
    tracker.update(timestamp=140.0, depth_cm=60.0, rain_mm_h=5.0)
    assert tracker.current_level == RiskLevel.CRITICAL
    assert tracker.lower_reading_count == 1
