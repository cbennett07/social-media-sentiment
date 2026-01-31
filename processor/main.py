import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from processor.config import ProcessorSettings
from processor.service import ProcessorService
from processor.queue import RedisQueueConsumer
from processor.llm.anthropic import AnthropicLLMClient
from processor.llm.openai import OpenAILLMClient
from processor.storage.s3 import S3ObjectStorage
from processor.storage.gcs import GCSObjectStorage
from processor.database.postgres import PostgresDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = ProcessorSettings()
app = FastAPI(title="Processor Service")


def build_llm_client():
    """Build the appropriate LLM client based on config."""
    if settings.llm_provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY required for Anthropic provider")
        return AnthropicLLMClient(
            api_key=settings.anthropic_api_key,
            model=settings.llm_model or "claude-sonnet-4-20250514"
        )
    elif settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY required for OpenAI provider")
        return OpenAILLMClient(
            api_key=settings.openai_api_key,
            model=settings.llm_model or "gpt-4o"
        )
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")


def build_service() -> ProcessorService:
    queue = RedisQueueConsumer(
        url=settings.redis_url,
        use_streams=settings.use_redis_streams
    )

    llm = build_llm_client()

    # Choose storage backend
    if settings.storage_provider == "gcs" or (
        settings.storage_provider == "auto" and not settings.storage_endpoint_url
    ):
        # Use GCS (default for GCP when no endpoint specified)
        storage = GCSObjectStorage(bucket=settings.storage_bucket)
    else:
        # Use S3-compatible storage (MinIO, AWS S3, etc.)
        storage = S3ObjectStorage(
            bucket=settings.storage_bucket,
            endpoint_url=settings.storage_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )

    database = PostgresDatabase(settings.database_url)

    return ProcessorService(
        queue=queue,
        llm=llm,
        storage=storage,
        database=database,
        topic=settings.queue_topic,
        skip_existing=settings.skip_existing
    )


# Lazy initialization
_service: ProcessorService | None = None


def get_service() -> ProcessorService:
    global _service
    if _service is None:
        _service = build_service()
    return _service


class ProcessRequest(BaseModel):
    batch_size: int | None = None


@app.post("/process")
def process(req: ProcessRequest, background_tasks: BackgroundTasks):
    """Trigger a processing batch."""
    service = get_service()
    batch_size = req.batch_size or settings.batch_size
    stats = service.process_batch(batch_size)
    return {"status": "completed", "stats": stats}


@app.post("/process/continuous")
def process_continuous(background_tasks: BackgroundTasks):
    """Start continuous processing in the background."""
    service = get_service()
    background_tasks.add_task(service.process_continuous, settings.batch_size)
    return {"status": "started", "message": "Continuous processing started in background"}


@app.get("/health")
def health():
    """Health check endpoint."""
    service = get_service()
    status = service.health()
    # Only require queue and database for startup health
    # LLM and storage are checked but not required
    healthy = status.get("queue", False) and status.get("database", False)
    if not healthy:
        raise HTTPException(status_code=503, detail=status)
    return status


if __name__ == "__main__":
    # CLI mode for continuous processing
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        service = build_service()
        service.process_continuous(settings.batch_size)
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8081)
