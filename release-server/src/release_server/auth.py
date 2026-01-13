from fastapi import HTTPException, Security, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from release_server.config import get_settings, Settings

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security), settings: Settings = Depends(get_settings)) -> str:
    """
    Verifies the Bearer token against the configured secret.
    """
    if credentials.credentials != settings.auth_token.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
