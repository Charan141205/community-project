"""
Configuration settings for flood-ews backend service.
Loaded from environment variables with sensible defaults for dev and production.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Service settings
    APP_NAME: str = "flood-ews"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/flood_ews"
    DB_POOL_MIN_SIZE: int = 2
    DB_POOL_MAX_SIZE: int = 10

    # MQTT Broker & Authentication
    MQTT_BROKER_HOST: str = "broker.hivemq.com"
    MQTT_BROKER_PORT: int = 1883
    MQTT_KEEPALIVE: int = 60
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_USE_TLS: bool = False
    MQTT_TOPIC_TELEMETRY: str = "flood/v1/+/telemetry"
    MQTT_TOPIC_STATUS: str = "flood/v1/+/status"
    MQTT_TOPIC_CMD: str = "flood/v1/{node_id}/cmd"

    # Operator Auth
    OPERATOR_API_KEY: str = "dev-operator-key-42"

    # Emergency Alert Dispatcher (Live Twilio & Multilingual)
    MOCK_ALERTS: bool = True
    ALERT_COOLDOWN_SECONDS: int = 900  # 15 minutes between alerts per node
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""  # e.g. whatsapp:+14155238886

    # Predictive Weather Integration (Open-Meteo & IMD)
    PREDICTIVE_WEATHER_ENABLED: bool = True
    WEATHER_API_LAT: float = 13.6288  # Tirupati Swarnamukhi River & Seshachalam Foothills center
    WEATHER_API_LON: float = 79.4192
    WEATHER_API_LOCATION_NAME: str = "Tirupati, Andhra Pradesh, India"
    WEATHER_CACHE_MINUTES: int = 30
    PREDICTIVE_RAIN_WATCH_THRESHOLD: float = 40.0  # mm/h forecast triggering pre-emptive WATCH

    # Evacuation & Geographic Settings
    EVACUATION_AVOIDANCE_RADIUS_M: float = 300.0
    PUBLIC_URL: str = "http://localhost:3000"

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
