"""
Configuration settings for flood-ews backend service.
Loaded from environment variables with sensible defaults.
"""

from typing import List
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

    # MQTT Broker
    MQTT_BROKER_HOST: str = "broker.hivemq.com"
    MQTT_BROKER_PORT: int = 1883
    MQTT_KEEPALIVE: int = 60
    MQTT_TOPIC_TELEMETRY: str = "flood/v1/+/telemetry"
    MQTT_TOPIC_STATUS: str = "flood/v1/+/status"
    MQTT_TOPIC_CMD: str = "flood/v1/{node_id}/cmd"

    # Operator Auth
    OPERATOR_API_KEY: str = "dev-operator-key-42"

    # Multilingual Alerts
    MOCK_ALERTS: bool = True
    ALERT_COOLDOWN_SECONDS: int = 900  # 15 minutes between alerts per node
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

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
