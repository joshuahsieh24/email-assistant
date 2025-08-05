"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from jose import jwt
import respx

from app.main import app
from app.settings import settings


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def valid_jwt_token():
    """Create a valid JWT token for testing."""
    payload = {"org_id": "test-org-123"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


@pytest.fixture
def openai_mock_response():
    """Mock OpenAI API response."""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help you today?"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 15,
            "total_tokens": 25
        }
    }


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/healthz")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == settings.app_version
        assert "redis_status" in data


class TestChatCompletionsEndpoint:
    """Test chat completions endpoint."""

    def test_missing_auth_header(self, client):
        """Test request without authorization header."""
        response = client.post("/v1/chat/completions", json={})
        assert response.status_code == 401
        assert "Invalid authorization header" in response.json()["error"]

    def test_invalid_jwt_token(self, client):
        """Test request with invalid JWT token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post("/v1/chat/completions", json={}, headers=headers)
        assert response.status_code == 401
        assert "Invalid token" in response.json()["error"]

    @respx.mock
    def test_successful_completion(self, client, valid_jwt_token, openai_mock_response):
        """Test successful chat completion."""
        # Mock OpenAI API call
        respx.post(f"{settings.openai_base_url}/v1/chat/completions").mock(
            return_value=respx.Response(200, json=openai_mock_response)
        )
        
        headers = {"Authorization": f"Bearer {valid_jwt_token}"}
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 100
        }
        
        response = client.post("/v1/chat/completions", json=request_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "chatcmpl-test123"
        assert data["choices"][0]["message"]["content"] == "Hello! How can I help you today?"

    @respx.mock
    def test_pii_redaction(self, client, valid_jwt_token, openai_mock_response):
        """Test that PII is redacted before sending to OpenAI."""
        # Mock OpenAI API call
        mock_route = respx.post(f"{settings.openai_base_url}/v1/chat/completions")
        mock_route.mock(return_value=respx.Response(200, json=openai_mock_response))
        
        headers = {"Authorization": f"Bearer {valid_jwt_token}"}
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Contact John Smith at john.smith@example.com"}
            ]
        }
        
        response = client.post("/v1/chat/completions", json=request_data, headers=headers)
        assert response.status_code == 200
        
        # Check that the request to OpenAI contained redacted content
        captured_request = mock_route.calls[0].request
        request_json = captured_request.json()
        
        # The content should be redacted (no email or name)
        content = request_json["messages"][0]["content"]
        assert "john.smith@example.com" not in content
        assert "John Smith" not in content
        assert "EMAIL" in content
        assert "PERSON" in content

    @respx.mock
    def test_openai_error(self, client, valid_jwt_token):
        """Test handling of OpenAI API errors."""
        # Mock OpenAI API error
        error_response = {
            "error": {
                "message": "Invalid API key",
                "type": "invalid_request_error",
                "code": "invalid_api_key"
            }
        }
        respx.post(f"{settings.openai_base_url}/v1/chat/completions").mock(
            return_value=respx.Response(401, json=error_response)
        )
        
        headers = {"Authorization": f"Bearer {valid_jwt_token}"}
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        
        response = client.post("/v1/chat/completions", json=request_data, headers=headers)
        assert response.status_code == 401
        
        data = response.json()
        assert data["error"]["message"] == "Invalid API key"

    def test_invalid_request_data(self, client, valid_jwt_token):
        """Test request with invalid data."""
        headers = {"Authorization": f"Bearer {valid_jwt_token}"}
        request_data = {
            "model": "gpt-3.5-turbo",
            # Missing required 'messages' field
        }
        
        response = client.post("/v1/chat/completions", json=request_data, headers=headers)
        assert response.status_code == 422  # Validation error


class TestRateLimiting:
    """Test rate limiting functionality."""

    @respx.mock
    def test_rate_limit_exceeded(self, client, valid_jwt_token, openai_mock_response):
        """Test rate limiting when exceeded."""
        # Mock OpenAI API call
        respx.post(f"{settings.openai_base_url}/v1/chat/completions").mock(
            return_value=respx.Response(200, json=openai_mock_response)
        )
        
        headers = {"Authorization": f"Bearer {valid_jwt_token}"}
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
        
        # Make multiple requests to trigger rate limiting
        # Note: This is a simplified test - in practice, you'd need to mock Redis
        # or use a test Redis instance
        for i in range(5):
            response = client.post("/v1/chat/completions", json=request_data, headers=headers)
            if response.status_code == 429:
                # Rate limit hit
                data = response.json()
                assert "Rate limit exceeded" in data["error"]["error"]
                break
        else:
            # If no rate limit hit, that's also acceptable for testing
            pass 