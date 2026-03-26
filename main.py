import os
from fastapi import FastAPI
from api.routers import router
from core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("startup")

app = FastAPI(
    title=settings.PROJECT_NAME, 
    version=settings.VERSION, 
    description="High-performance, low-memory PDF Extraction Microservice"
)

# Connect the routers
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    port = os.environ.get("PORT", default="8000")
    logger.info("=====================================================")
    logger.info(f"🚀 PDF Extract Service Started on Port {port}")
    logger.info("=====================================================")
    logger.info(f"✅ Health Check endpoint   : GET  http://0.0.0.0:{port}/health")
    logger.info(f"📄 PDF Extract endpoint    : POST http://0.0.0.0:{port}/extract-pdf")
    logger.info(f"📘 Swagger Documentation   : GET  http://0.0.0.0:{port}/docs")
    logger.info("=====================================================")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    # Optimized serving without extra features keeping RAM low
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=settings.DEBUG, workers=1)
