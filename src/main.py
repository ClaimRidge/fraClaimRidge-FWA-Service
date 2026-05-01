from fastapi import FastAPI
from src.api import router as api_router
from src.api import dashboard
from src.config import settings
import structlog
from contextlib import asynccontextmanager

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("service_starting", service=settings.SERVICE_NAME, env=settings.ENV)
    
    # Initialize Kafka Consumer (Background Task)
    # import asyncio
    # from src.dependencies import get_kafka_consumer
    # consumer = get_kafka_consumer()
    # asyncio.create_task(consumer.start())
    
    yield
    
    # Shutdown logic
    logger.info("service_stopping")

app = FastAPI(
    title="ClaimRidge Fraud Waste Abuse Service",
    description="Production-grade insurance fraud detection microservice",
    version="0.1.0",
    lifespan=lifespan
)

# Mount Routers
app.include_router(api_router.router)
app.include_router(dashboard.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
