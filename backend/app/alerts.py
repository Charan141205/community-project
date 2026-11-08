"""
Multilingual Alert Dispatcher & Notification Engine.
Supports English, Telugu, and Hindi with per-node 15-minute rate limiting and provider abstraction.
"""

import abc
import logging
import time
from typing import Dict, List, Optional
from backend.app.config import settings

logger = logging.getLogger("flood_alerts")


class AlertProvider(abc.ABC):
    @abc.abstractmethod
    async def send_message(self, recipient_phone: str, message: str, channel: str = "sms") -> bool:
        """Send notification via provider channel."""
        pass


class MockProvider(AlertProvider):
    """Logs alerts to console and records them into database."""

    async def send_message(self, recipient_phone: str, message: str, channel: str = "sms") -> bool:
        logger.info(f"📢 [MOCK {channel.upper()}] To: {recipient_phone} | Content: {message}")
        return True


class TwilioProvider(AlertProvider):
    """Dispatches real SMS or WhatsApp alerts via Twilio API."""

    def __init__(self, account_sid: str, auth_token: str, from_phone: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_phone = from_phone

    async def send_message(self, recipient_phone: str, message: str, channel: str = "sms") -> bool:
        if not self.account_sid or not self.auth_token:
            logger.warning("Twilio credentials not configured, skipping live dispatch.")
            return False

        try:
            import httpx
            from_number = f"whatsapp:{self.from_phone}" if channel == "whatsapp" else self.from_phone
            to_number = f"whatsapp:{recipient_phone}" if channel == "whatsapp" else recipient_phone

            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    url,
                    data={"From": from_number, "To": to_number, "Body": message},
                    auth=(self.account_sid, self.auth_token),
                    timeout=10.0,
                )
                return resp.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Failed to dispatch Twilio alert to {recipient_phone}: {e}")
            return False


class AlertManager:
    """
    Manages rate-limiting (max 1 alert per node per 15 min),
    multilingual templates (EN/TE/HI), and dispatching.
    """

    def __init__(self, provider: Optional[AlertProvider] = None, cooldown_seconds: int = 900):
        self.provider = provider or MockProvider()
        self.cooldown_seconds = cooldown_seconds
        # Tracks timestamp of last sent alert per node_id
        self.last_alert_time: Dict[str, float] = {}

    def should_send_alert(self, node_id: str, current_time: Optional[float] = None) -> bool:
        """Rate limit: enforce 15-minute cooldown between alerts for the same node."""
        now = current_time if current_time is not None else time.time()
        last_time = self.last_alert_time.get(node_id, 0.0)
        return (now - last_time) >= self.cooldown_seconds

    def format_message(
        self,
        language: str,
        level: str,
        node_name: str,
        ward: str,
        ratio: float,
        rain_mm_h: float,
        evac_link: str,
    ) -> str:
        """Format localized disaster early warning message."""
        ratio_pct = int(ratio * 100)

        if language == "te":
            # Telugu
            msg = (
                f"🚨 వరద హెచ్చరిక [{level}]: {ward} లోని {node_name} వద్ద నీటిమట్టం {ratio_pct}% చేరింది "
                f"(వర్షం: {rain_mm_h:.1f} మి.మీ/గం)."
            )
            if level in ["WARNING", "CRITICAL"]:
                msg += f" సురక్షిత తరలింపు మార్గం & పునరావాస కేంద్రాలు: {evac_link}"
            return msg

        elif language == "hi":
            # Hindi
            msg = (
                f"🚨 बाढ़ चेतावनी [{level}]: {ward} के {node_name} में जलस्तर {ratio_pct}% पहुंच गया है "
                f"(बारिश: {rain_mm_h:.1f} मिमी/घंटा)।"
            )
            if level in ["WARNING", "CRITICAL"]:
                msg += f" सुरक्षित निकासी मार्ग और राहत शिविर: {evac_link}"
            return msg

        else:
            # English (Default)
            msg = (
                f"🚨 FLOOD ALERT [{level}]: Water level in {node_name} ({ward}) has reached {ratio_pct}% capacity "
                f"(Rain: {rain_mm_h:.1f} mm/h)."
            )
            if level in ["WARNING", "CRITICAL"]:
                msg += f" Safe evacuation routes & relief shelters: {evac_link}"
            return msg

    def record_alert_sent(self, node_id: str, sent_time: Optional[float] = None):
        """Record timestamp of sent alert for rate-limiting."""
        now = sent_time if sent_time is not None else time.time()
        self.last_alert_time[node_id] = now


# Global Alert Manager Singleton
alert_manager = AlertManager(
    provider=MockProvider() if settings.MOCK_ALERTS else TwilioProvider(
        settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER
    ),
    cooldown_seconds=settings.ALERT_COOLDOWN_SECONDS,
)
