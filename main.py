from fastapi import FastAPI
from api.routers import router
from core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME, 
    version=settings.VERSION, 
    description="High-performance, low-memory PDF Extraction Microservice"
)

# Connect the routers
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    # Optimized serving without extra features keeping RAM low
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=settings.DEBUG, workers=1)
