"""
Multilingual Alert Dispatcher & Notification Engine.
Supports Live Twilio SMS & WhatsApp Business API, Mock Provider,
and per-node 15-minute rate limiting with English, Telugu, and Hindi localization.
"""

import abc
import asyncio
import logging
import time
from typing import Dict, List, Optional
from backend.app.config import settings

logger = logging.getLogger("flood_alerts")


class AlertProvider(abc.ABC):
    @abc.abstractmethod
    async def send_message(self, recipient_phone: str, message: str, channel: str = "sms") -> bool:
        """Send notification via provider channel ('sms' or 'whatsapp')."""
        pass


class MockProvider(AlertProvider):
    """Logs alerts to console and records them into database (Default for dev/testing)."""

    async def send_message(self, recipient_phone: str, message: str, channel: str = "sms") -> bool:
        logger.info(f"📢 [MOCK {channel.upper()}] To: {recipient_phone} | Content: {message}")
        return True


class TwilioProvider(AlertProvider):
    """
    Live production provider for Twilio SMS and WhatsApp notifications.
    Supports official Twilio Client with async executor and direct async fallback.
    """

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_sms_phone: str,
        from_whatsapp_phone: str = "",
    ):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_sms_phone = from_sms_phone
        self.from_whatsapp_phone = from_whatsapp_phone or from_sms_phone

        self.client = None
        if self.account_sid and self.auth_token:
            try:
                from twilio.rest import Client
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Initialized live Twilio Client.")
            except ImportError:
                logger.warning("Twilio SDK not installed, using direct async HTTP.")

    async def send_message(self, recipient_phone: str, message: str, channel: str = "sms") -> bool:
        if not self.account_sid or not self.auth_token:
            logger.warning("Twilio credentials not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.")
            return False

        is_whatsapp = (channel.lower() == "whatsapp")

        # Format E.164 numbers
        if is_whatsapp:
            from_addr = (
                self.from_whatsapp_phone
                if self.from_whatsapp_phone.startswith("whatsapp:")
                else f"whatsapp:{self.from_whatsapp_phone}"
            )
            to_addr = (
                recipient_phone
                if recipient_phone.startswith("whatsapp:")
                else f"whatsapp:{recipient_phone}"
            )
        else:
            from_addr = self.from_sms_phone
            to_addr = recipient_phone

        # 1. Use Twilio Python SDK in async thread pool if available
        if self.client:
            try:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.client.messages.create(
                        body=message,
                        from_=from_addr,
                        to=to_addr,
                    ),
                )
                logger.info(f"✅ Twilio {channel.upper()} dispatched! SID: {result.sid} to {to_addr}")
                return True
            except Exception as e:
                logger.error(f"❌ Twilio SDK dispatch failed: {e}")
                # Fall through to direct HTTP fallback

        # 2. Direct HTTP Basic Auth Fallback (via httpx)
        try:
            import httpx
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
            async with httpx.AsyncClient(timeout=10.0) as http_client:
                resp = await http_client.post(
                    url,
                    data={"From": from_addr, "To": to_addr, "Body": message},
                    auth=(self.account_sid, self.auth_token),
                )
                if resp.status_code in [200, 201]:
                    logger.info(f"✅ Twilio direct HTTP {channel.upper()} sent to {to_addr}")
                    return True
                else:
                    logger.error(f"❌ Twilio HTTP Error ({resp.status_code}): {resp.text}")
                    return False
        except Exception as ex:
            logger.error(f"❌ Twilio direct HTTP dispatch failed: {ex}")
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


def create_default_alert_manager() -> AlertManager:
    """Factory to instantiate the appropriate provider based on settings."""
    if not settings.MOCK_ALERTS and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        provider = TwilioProvider(
            account_sid=settings.TWILIO_ACCOUNT_SID,
            auth_token=settings.TWILIO_AUTH_TOKEN,
            from_sms_phone=settings.TWILIO_PHONE_NUMBER,
            from_whatsapp_phone=settings.TWILIO_WHATSAPP_NUMBER,
        )
    else:
        provider = MockProvider()

    return AlertManager(provider=provider, cooldown_seconds=settings.ALERT_COOLDOWN_SECONDS)


# Global Alert Manager Singleton
alert_manager = create_default_alert_manager()


async def send_multilingual_alert(
    node_id: str,
    node_name: str,
    ward: str,
    level: str,
    ratio: float,
    rain_mm_h: float,
    evac_link: str,
    subscribers: Optional[List[Dict]] = None,
) -> int:
    """
    Top-level production helper to dispatch localized SMS and WhatsApp alerts to citizens.
    Uses live TwilioProvider when credentials are configured, or MockProvider for development.
    Dispatches alerts in Telugu, Hindi, and English with dynamic evacuation shelter links.
    """
    if not alert_manager.should_send_alert(node_id):
        logger.info(f"Alert for [{node_id}] suppressed by 15-minute rate-limiting cooldown.")
        return 0

    alert_manager.record_alert_sent(node_id)
    if subscribers is None:
        from backend.app.db import db
        subscribers = await db.get_subscribers_by_ward(ward)

    dispatched = 0
    for sub in subscribers:
        lang = sub.get("language", "en")
        phone = sub.get("phone", "")
        if not phone:
            continue

        msg = alert_manager.format_message(
            language=lang,
            level=level,
            node_name=node_name,
            ward=ward,
            ratio=ratio,
            rain_mm_h=rain_mm_h,
            evac_link=evac_link,
        )

        # Dispatch via live Twilio SMS or WhatsApp
        channel = "whatsapp" if sub.get("preferred_channel") == "whatsapp" else "sms"
        success = await alert_manager.provider.send_message(phone, msg, channel=channel)
        if success:
            dispatched += 1

    return dispatched

