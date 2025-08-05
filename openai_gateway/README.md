# OpenAI Gateway - Secure Proxy for Salesforce AI Email Assistant

A production-grade Python microservice that acts as a secure gateway between Salesforce and OpenAI, providing PII redaction, audit logging, rate limiting, and JWT authentication.

## Features

- 🔒 **PII Redaction**: Automatically detects and redacts sensitive data (emails, names, phone numbers) before sending to OpenAI
- 🔄 **Re-identification**: Restores original PII values in responses
- 🚦 **Rate Limiting**: Per-organization rate limiting using Redis token bucket algorithm
- 🔐 **JWT Authentication**: Secure API access with JWT tokens
- 📊 **Audit Logging**: Structured logging with no sensitive data exposure
- 🐳 **Docker Ready**: Complete Docker and docker-compose setup
- 🧪 **Comprehensive Testing**: Unit and integration tests with pytest
- ⚡ **High Performance**: Async FastAPI with httpx for HTTP calls

## Architecture

```
Salesforce → OpenAI Gateway → OpenAI API
                ↓
            PII Redaction
                ↓
            Rate Limiting
                ↓
            Audit Logging
                ↓
            Response Re-identification
```

## Quick Start

### Prerequisites

- Python 3.12+
- Redis
- OpenAI API key
- Poetry (for dependency management)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd openai_gateway
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Start Redis**
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

5. **Run the application**
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

### Docker Development

1. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

2. **Start services**
   ```bash
   docker-compose up --build
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `HOST` | Application host | `0.0.0.0` |
| `PORT` | Application port | `8000` |
| `OPENAI_BASE_URL` | OpenAI API base URL | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `JWT_SECRET_KEY` | JWT signing secret | Required |
| `RATE_LIMIT_REQUESTS` | Requests per window | `60` |
| `RATE_LIMIT_WINDOW_SECONDS` | Rate limit window | `60` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FORMAT` | Log format (json/console) | `json` |

### JWT Token Generation

Generate JWT tokens for your Salesforce orgs:

```python
from jose import jwt
import time

# Create JWT token
payload = {
    "org_id": "your-salesforce-org-id",
    "exp": time.time() + (60 * 60),  # 1 hour expiry
    "iat": time.time()
}

token = jwt.encode(payload, "your-jwt-secret-key", algorithm="HS256")
print(f"Bearer {token}")
```

## API Endpoints

### Health Check
```http
GET /healthz
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "redis_status": "connected"
}
```

### Chat Completions (OpenAI Proxy)
```http
POST /v1/chat/completions
Authorization: Bearer <jwt-token>
Content-Type: application/json

{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "user", "content": "Contact John at john@example.com"}
  ],
  "max_tokens": 100
}
```

The gateway will:
1. Redact PII: `"Contact PERSON at EMAIL"`
2. Forward to OpenAI
3. Re-identify in response: `"Contact John at john@example.com"`

## Salesforce Integration

### 1. Update Named Credential

In Salesforce Setup, update your Named Credential:

- **Label**: OpenAI Gateway
- **Name**: `OpenAI_Gateway`
- **URL**: `https://your-gateway-domain.com`
- **Identity Type**: Named Principal
- **Authentication Protocol**: No Authentication

### 2. Update Apex Code

Update your `AIEmailService.cls`:

```apex
private static String callOpenAI(String prompt) {
    HttpRequest req = new HttpRequest();
    req.setEndpoint('callout:OpenAI_Gateway/v1/chat/completions');
    req.setMethod('POST');
    req.setHeader('Content-Type', 'application/json');
    req.setHeader('Authorization', 'Bearer ' + Label.OpenAI_Gateway_JWT);
    
    // ... rest of your code remains the same
}
```

### 3. Create Custom Label

Create a Custom Label `OpenAI_Gateway_JWT` with your JWT token.

## Testing

### Run Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_redaction.py
```

### Manual Testing

1. **Generate a JWT token**
2. **Test health endpoint**
   ```bash
   curl http://localhost:8000/healthz
   ```

3. **Test chat completions**
   ```bash
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [
         {"role": "user", "content": "Contact John at john@example.com"}
       ]
     }'
   ```

## Deployment

### Docker Production

1. **Build image**
   ```bash
   docker build -t openai-gateway .
   ```

2. **Run container**
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e OPENAI_API_KEY=your_key \
     -e JWT_SECRET_KEY=your_secret \
     -e REDIS_URL=redis://redis:6379 \
     openai-gateway
   ```

### AWS ECS (Terraform)

The `terraform/` directory contains infrastructure as code for deploying to AWS ECS with API Gateway, Redis ElastiCache, and VPC.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Security Features

- **PII Redaction**: Uses Microsoft Presidio to detect and redact sensitive data
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Per-organization rate limiting with Redis
- **Audit Logging**: Structured logs without sensitive data
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Comprehensive error handling and logging

## Monitoring

### Health Checks
- Application health: `GET /healthz`
- Redis connectivity
- OpenAI API connectivity

### Logging
- Structured JSON logging
- Request/response metadata
- Performance metrics
- Error tracking

### Metrics
- Request latency
- Token usage
- Rate limit status
- Error rates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run linting: `poetry run black . && poetry run isort .`
6. Submit a pull request

## License

MIT License - see LICENSE file for details. 