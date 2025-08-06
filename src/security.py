from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from .database.db_access_objects.app_dao import AppDAO
from src.logger import get_logger

bearer_scheme = HTTPBearer()
app_dao = AppDAO()

logger = get_logger(__name__)

def get_current_app(auth: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = auth.credentials
        logger.info("Decoding JWT token for authentication.")
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        app_id = unverified_payload.get("app_id")
        if app_id is None:
            logger.error("JWT missing app_id.")
            raise credentials_exception

    except jwt.PyJWTError:
        logger.error("JWT decode error.")
        raise credentials_exception

    logger.info(f"Fetching app record for app_id={app_id}")
    app_record = app_dao.get_by_id(app_id)
    if app_record is None:
        logger.error(f"App not found for app_id={app_id}")
        raise credentials_exception

    api_key = app_record.api_key
    if api_key is None:
        logger.error(f"API key missing for app_id={app_id}")
        raise credentials_exception

    try:
        logger.info(f"Verifying JWT signature for app_id={app_id}")
        payload = jwt.decode(token, api_key, algorithms=["HS256"])
        return payload

    except jwt.ExpiredSignatureError:
        logger.error(f"JWT expired for app_id={app_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        logger.error(f"JWT verification failed for app_id={app_id}")
        raise credentials_exception
