"""Simple FastAPI app for Railway deployment."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create FastAPI app
app = FastAPI(
    title="OpenAI Gateway",
    version="0.1.0",
)

@app.get("/healthz")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "version": "0.1.0",
            "redis_status": "unavailable"
        }
    )

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "OpenAI Gateway is running!"} 