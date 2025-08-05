"""FastAPI application for OpenAI proxy gateway."""

import json
import time
from typing import Dict, Any

import httpx
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jose import JWTError, jwt

from .models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    HealthResponse,
    ErrorResponse,
)
from .settings import settings
from .logging import (
    setup_logging,
    get_logger,
    log_request,
    log_response,
    log_openai_request,
    log_openai_response,
)
from .redaction import redactor
from .reidentify import reidentifier
from .rate_limit import redis_manager


# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_jwt_token(request: Request) -> str:
    """Verify JWT token and extract org_id."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        org_id = payload.get("org_id")
        if not org_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return org_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def check_rate_limit(org_id: str) -> None:
    """Check rate limit for the organization."""
    rate_limiter = redis_manager.get_rate_limiter()
    
    if not await rate_limiter.is_allowed(org_id):
        remaining = await rate_limiter.get_remaining_requests(org_id)
        reset_time = await rate_limiter.get_reset_time(org_id)
        
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "remaining": remaining,
                "reset_time": reset_time,
            }
        )


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        await redis_manager.connect()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    await redis_manager.disconnect()
    logger.info("Application shutdown complete")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses."""
    start_time = time.time()
    
    # Extract org_id from JWT if available
    org_id = None
    try:
        org_id = await verify_jwt_token(request)
    except HTTPException:
        pass  # Not all endpoints require auth
    
    # Log request
    log_request(
        logger,
        method=request.method,
        path=request.url.path,
        org_id=org_id,
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate latency
    latency = (time.time() - start_time) * 1000
    
    # Log response
    log_response(
        logger,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        org_id=org_id,
        latency_ms=latency,
    )
    
    return response


@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    redis_status = "connected" if await redis_manager.is_connected() else "disconnected"
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        redis_status=redis_status,
    )


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    org_id: str = Depends(verify_jwt_token),
):
    """
    OpenAI chat completions proxy endpoint.
    
    This endpoint:
    1. Redacts PII from the request
    2. Forwards to OpenAI
    3. Re-identifies PII in the response
    4. Returns the result
    """
    start_time = time.time()
    
    # Check rate limit
    await check_rate_limit(org_id)
    
    try:
        # Convert request to dict for processing
        request_dict = request.dict()
        
        # Redact PII from messages
        redacted_messages, token_mappings = redactor.redact_messages(
            request_dict["messages"]
        )
        
        # Update request with redacted messages
        request_dict["messages"] = redacted_messages
        
        # Log OpenAI request (no sensitive data)
        log_openai_request(
            logger,
            org_id=org_id,
            prompt_tokens=len(str(request_dict["messages"])),
        )
        
        # Forward to OpenAI
        async with httpx.AsyncClient() as client:
            openai_response = await client.post(
                f"{settings.openai_base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json=request_dict,
                timeout=30.0,
            )
        
        # Calculate latency
        latency = (time.time() - start_time) * 1000
        
        if openai_response.status_code != 200:
            # Log error response
            logger.error(
                "OpenAI API error",
                org_id=org_id,
                status_code=openai_response.status_code,
                response_text=openai_response.text,
            )
            
            return JSONResponse(
                status_code=openai_response.status_code,
                content=openai_response.json(),
            )
        
        # Parse OpenAI response
        response_data = openai_response.json()
        
        # Log OpenAI response (no sensitive data)
        response_tokens = response_data.get("usage", {}).get("completion_tokens", 0)
        log_openai_response(
            logger,
            org_id=org_id,
            response_tokens=response_tokens,
            latency_ms=latency,
        )
        
        # Re-identify PII in response
        reidentified_response = reidentifier.reidentify_openai_response(
            response_data, token_mappings
        )
        
        return reidentified_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", org_id=org_id)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    ) 