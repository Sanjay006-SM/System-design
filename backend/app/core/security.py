from datetime import datetime, timedelta
from typing import Optional
import hmac
import hashlib
import json
import base64
from fastapi import Header, HTTPException, status, Depends
from backend.app.core.config import settings

def create_access_token(user_id: int, username: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp()
    }
    header = {"alg": "HS256", "typ": "JWT"}
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signing_input = f"{header_b64}.{payload_b64}"
    
    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        signing_input.encode(),
        hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_token(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token segments")
        
        signing_input = f"{parts[0]}.{parts[1]}"
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode(),
            signing_input.encode(),
            hashlib.sha256
        ).digest()
        expected_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        
        if not hmac.compare_digest(parts[2], expected_b64):
            raise ValueError("Signature mismatch")
        
        # Add padding back if necessary
        payload_b64 = parts[1]
        padding = len(payload_b64) % 4
        if padding:
            payload_b64 += "=" * (4 - padding)
        
        payload_data = json.loads(base64.urlsafe_b64decode(payload_b64.encode()).decode())
        if payload_data.get("exp", 0) < datetime.utcnow().timestamp():
            raise ValueError("Token expired")
            
        return payload_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
        )

def get_current_user_id(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    x_demo_user_id: Optional[str] = Header(None, alias="X-Demo-User-Id")
) -> int:
    """
    Production JWT validation with development/demo fallback.
    If Authorization header is provided: verifies JWT Bearer token.
    If in development and X-Demo-User-Id is provided: allows authenticated demo mode.
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = verify_token(token)
        return int(payload["sub"])
    
    # Development demo mode
    if settings.DEBUG and x_demo_user_id:
        try:
            return int(x_demo_user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="X-Demo-User-Id header must be an integer"
            )
            
    # Default to unauthenticated exception if no valid token or dev demo provided
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide 'Authorization: Bearer <token>' or demo credentials header 'X-Demo-User-Id'"
    )
