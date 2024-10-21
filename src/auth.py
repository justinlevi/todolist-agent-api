from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.status import HTTP_403_FORBIDDEN
from src.config import settings

security = HTTPBearer()

async def get_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials == settings.API_KEY or settings.ENVIRONMENT == "test":
        return credentials.credentials
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )
