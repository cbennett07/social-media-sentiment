from pydantic_settings import BaseSettings


class ProcessorSettings(BaseSettings):
    # Queue
    redis_url: str = "redis://localhost:6379"
    queue_topic: str = "raw_content"
    use_redis_streams: bool = False

    # LLM
    llm_provider: str = "anthropic"  # "anthropic" or "openai"
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    llm_model: str | None = None  # Uses provider default if not set

    # Object Storage (S3-compatible)
    storage_bucket: str = "sentiment-raw-content"
    storage_endpoint_url: str | None = None  # For MinIO, GCS interop, etc.
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_region: str = "us-east-1"

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/sentiment"

    # Processing
    batch_size: int = 10
    skip_existing: bool = True

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        extra = "ignore"
