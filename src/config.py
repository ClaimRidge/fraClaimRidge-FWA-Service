from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Service Info
    SERVICE_NAME: str = "fwa-svc"
    ENV: str = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/claimbridge_fwa"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_GROUP_ID: str = "fwa-svc"
    CLAIMS_TOPIC_PREFIX: str = "tenant"  # Final topic: {tenant}.claims.submitted
    FRAUD_FLAGS_TOPIC: str = "fraud.flags"
    FRAUD_CASES_TOPIC: str = "fraud.cases"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Temporal
    TEMPORAL_URL: str = "localhost:7233"
    TEMPORAL_NAMESPACE: str = "default"
    TEMPORAL_TASK_QUEUE: str = "fwa-task-queue"

    # MLflow
    MLFLOW_TRACKING_URI: Optional[str] = None
    MLFLOW_MODEL_ALIAS: str = "champion"

    # Security
    JWT_SECRET_KEY: str = "super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"

    # FWA Logic
    L1_ANOMALY_THRESHOLD: float = 0.85
    L2_DRIFT_THRESHOLD: float = 0.2
    AUTO_CASE_SEVERITY_THRESHOLD: str = "HIGH"

settings = Settings()
