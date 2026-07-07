from fastapi import HTTPException, Depends, Security
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings
from typing import Optional

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

async def verify_token(credentials: HTTPAuthCredentials = Security(security)) -> dict:
    """Verify JWT token and return claims."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, **payload}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

async def get_current_user(token: dict = Depends(verify_token)) -> dict:
    """Get current user from token."""
    return token
