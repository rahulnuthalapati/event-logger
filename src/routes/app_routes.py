from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
import uuid
from datetime import datetime 

from src.database.db_access_objects.app_dao import AppDAO
from src.database.db_access_objects.app_record import AppRecord
from src.logger import get_logger


router = APIRouter()

logger = get_logger(__name__)

class AppRegistrationRequest(BaseModel):
    name: str

@router.post("/register")
def register_app(request: AppRegistrationRequest):
    """
    Registers a new application and returns a JWT for it.
    """
    try:
        logger.info(f"Registering new app: {request.name}")
        app_dao = AppDAO()
        new_app_record = AppRecord(
            name=request.name,
            api_key=str(uuid.uuid4()),
            created_at=datetime.now()
        )
        
        new_app = app_dao.create(new_app_record)
        app_id = new_app.id
        api_key = new_app.api_key

        payload = {
            "app_id": app_id,
            "name": request.name
        }

        token = jwt.encode(payload, api_key, algorithm="HS256")
        logger.info(f"App registered successfully: app_id={app_id}")

        return JSONResponse(
            status_code=201,
            content={
                "message": "Application registered successfully.",
                "app_name": request.name,
                "token": token
            }
        )
    except ValueError as ve:
        logger.error(f"App registration failed: {ve}")
        raise HTTPException(status_code=409, detail=str(ve))
    except Exception as e:
        logger.error(f"App registration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

