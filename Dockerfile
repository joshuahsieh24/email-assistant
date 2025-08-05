FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY openai_gateway/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY openai_gateway/ .

# Expose the port
EXPOSE 8000

# Start the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 