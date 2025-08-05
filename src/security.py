# src/security.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from .database.db_access_objects.app_dao import AppDAO

# This scheme will handle extracting the "Bearer <token>" from the Authorization header
bearer_scheme = HTTPBearer()

# Instantiate the DAO to be used within this module
app_dao = AppDAO()

def get_current_app(auth: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """
    Dependency to verify JWT and return the app's payload.

    1. Decodes JWT to get app_id without verifying the signature.
    2. Fetches the app's real API key from the database using the app_id.
    3. Verifies the JWT signature using the fetched API key.
    4. Raises HTTPException if the token is invalid in any way.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # The actual token string is in auth.credentials
        token = auth.credentials
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        app_id = unverified_payload.get("app_id")
        if app_id is None:
            raise credentials_exception

    except jwt.PyJWTError:
        # This catches any error during the initial decoding
        raise credentials_exception

    # Safely fetch the app record from the database
    app_record = app_dao.get_by_id(app_id)
    if app_record is None:
        # This means the app referenced in the token doesn't exist.
        raise credentials_exception

    # Now get the api_key from the record
    api_key = app_record.api_key
    if api_key is None:
        # Should not happen if your DB constraints are correct, but a good safety check
        raise credentials_exception

    try:
        # Finally, verify the token's signature using the secret key we just fetched
        payload = jwt.decode(token, api_key, algorithms=["HS256"])
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception
