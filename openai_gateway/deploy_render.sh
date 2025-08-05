#!/bin/bash

echo "🚀 Deploying OpenAI Gateway to Render..."

# Create a new web service on Render
curl -X POST "https://api.render.com/v1/services" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "openai-gateway",
    "type": "web",
    "env": "python",
    "buildCommand": "pip install -r requirements.txt",
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "planId": "starter"
  }'

echo "✅ Deployment initiated! Check your Render dashboard." 