"""Pydantic models for OpenAI API request/response schemas."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    """OpenAI message model."""
    
    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    """OpenAI chat completion request model."""
    
    model: str = Field(..., description="Model to use for completion")
    messages: List[Message] = Field(..., description="List of messages")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(None, description="Sampling temperature")
    top_p: Optional[float] = Field(None, description="Nucleus sampling parameter")
    n: Optional[int] = Field(None, description="Number of completions")
    stream: Optional[bool] = Field(None, description="Stream response")
    stop: Optional[List[str]] = Field(None, description="Stop sequences")
    presence_penalty: Optional[float] = Field(None, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(None, description="Frequency penalty")
    logit_bias: Optional[Dict[str, float]] = Field(None, description="Logit bias")
    user: Optional[str] = Field(None, description="User identifier")


class Choice(BaseModel):
    """OpenAI choice model."""
    
    index: int = Field(..., description="Choice index")
    message: Message = Field(..., description="Generated message")
    finish_reason: Optional[str] = Field(None, description="Finish reason")


class Usage(BaseModel):
    """OpenAI usage model."""
    
    prompt_tokens: int = Field(..., description="Prompt tokens used")
    completion_tokens: int = Field(..., description="Completion tokens used")
    total_tokens: int = Field(..., description="Total tokens used")


class ChatCompletionResponse(BaseModel):
    """OpenAI chat completion response model."""
    
    id: str = Field(..., description="Response ID")
    object: str = Field(..., description="Object type")
    created: int = Field(..., description="Creation timestamp")
    model: str = Field(..., description="Model used")
    choices: List[Choice] = Field(..., description="Generated choices")
    usage: Usage = Field(..., description="Token usage")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: Dict[str, Any] = Field(..., description="Error details")


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    redis_status: str = Field(..., description="Redis connection status")


class TokenMap(BaseModel):
    """Token mapping for PII redaction/re-identification."""
    
    original_text: str = Field(..., description="Original text")
    token_id: str = Field(..., description="Token ID")
    entity_type: str = Field(..., description="Entity type")
    confidence: float = Field(..., description="Confidence score") 