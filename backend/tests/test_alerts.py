"""
Unit tests for the Alert Manager:
Rate-limiting (15-minute cooldown), multilingual templating (English, Telugu, Hindi).
"""

import pytest
from backend.app.alerts import AlertManager, MockProvider


def test_alert_rate_limiting():
    mgr = AlertManager(provider=MockProvider(), cooldown_seconds=900)
    node_id = "drain-01"
    t0 = 1000.0

    # First alert should be permitted
    assert mgr.should_send_alert(node_id, current_time=t0) is True
    mgr.record_alert_sent(node_id, sent_time=t0)

    # 5 minutes later (300s): should be blocked by cooldown
    assert mgr.should_send_alert(node_id, current_time=t0 + 300.0) is False

    # 14.5 minutes later (870s): still blocked
    assert mgr.should_send_alert(node_id, current_time=t0 + 870.0) is False

    # 15.1 minutes later (905s): cooldown expired, should be permitted
    assert mgr.should_send_alert(node_id, current_time=t0 + 905.0) is True


def test_multilingual_formatting_english():
    mgr = AlertManager()
    msg = mgr.format_message(
        language="en",
        level="WARNING",
        node_name="Moosarambagh Bridge",
        ward="Amberpet",
        ratio=0.76,
        rain_mm_h=24.5,
        evac_link="http://localhost:3000/public?evac=true",
    )
    assert "FLOOD ALERT [WARNING]" in msg
    assert "Moosarambagh Bridge" in msg
    assert "76%" in msg
    assert "http://localhost:3000/public?evac=true" in msg


def test_multilingual_formatting_telugu():
    mgr = AlertManager()
    msg = mgr.format_message(
        language="te",
        level="CRITICAL",
        node_name="చాదర్‌ఘాట్ వంతెన",
        ward="మలక్‌పేట్",
        ratio=0.89,
        rain_mm_h=55.0,
        evac_link="http://localhost:3000/public?evac=true",
    )
    assert "వరద హెచ్చరిక [CRITICAL]" in msg
    assert "చాదర్‌ఘాట్ వంతెన" in msg
    assert "89%" in msg
    assert "సురక్షిత తరలింపు మార్గం" in msg


def test_multilingual_formatting_hindi():
    mgr = AlertManager()
    msg = mgr.format_message(
        language="hi",
        level="CRITICAL",
        node_name="मूसारामबाग पुल",
        ward="अंबरपेट",
        ratio=0.92,
        rain_mm_h=60.0,
        evac_link="http://localhost:3000/public?evac=true",
    )
    assert "बाढ़ चेतावनी [CRITICAL]" in msg
    assert "मूसारामबाग पुल" in msg
    assert "92%" in msg
    assert "सुरक्षित निकासी मार्ग" in msg
