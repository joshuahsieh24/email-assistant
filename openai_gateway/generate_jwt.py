#!/usr/bin/env python3
"""Generate JWT token for Salesforce authentication."""

import jwt
import time
from datetime import datetime, timedelta

# Configuration - update these values
JWT_SECRET_KEY = "your-super-long-random-secret-key-here-make-it-long-and-random"  # Same as in .env
ORG_ID = "00D01000001JOk5EAG"  # Your Salesforce org ID from the console logs
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

def generate_jwt_token(org_id: str, secret_key: str, expire_minutes: int = 60) -> str:
    """Generate a JWT token for the specified org."""
    payload = {
        "org_id": org_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=expire_minutes)
    }
    
    token = jwt.encode(payload, secret_key, algorithm=JWT_ALGORITHM)
    return token

if __name__ == "__main__":
    # Generate token
    token = generate_jwt_token(ORG_ID, JWT_SECRET_KEY, JWT_EXPIRE_MINUTES)
    
    print("Generated JWT Token:")
    print(f"Bearer {token}")
    print("\nUse this token in your Salesforce Apex code")
    print(f"Token expires in {JWT_EXPIRE_MINUTES} minutes")
    print(f"Org ID: {ORG_ID}") 