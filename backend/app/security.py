from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer
from typing import Optional

security = HTTPBearer()

async def verify_token(credentials: Optional[str] = Security(security)) -> str:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return credentials.credentials
