from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import hashlib
import json

from src.security import get_current_app
from src.database.db_access_objects.event_dao import EventDAO
from src.database.db_access_objects.event_record import EventRecord
from src.logger import get_logger

router = APIRouter()
event_dao = EventDAO()
logger = get_logger(__name__)

class EventPayload(BaseModel):
    type: str = Field(..., min_length=1, max_length=64, description="The type of the event.")
    source: Optional[str] = Field(None, max_length=128, description="The source or origin of the event.")
    data: Dict[str, Any] = Field(default_factory=dict, description="The main JSON data payload of the event.")

@router.post("/event", status_code=201)
def log_event(
    event_payload: EventPayload, # Use the Pydantic model here instead of Dict
    current_app: dict = Depends(get_current_app)
):
    """
    Logs an event. This endpoint is protected and requires a valid JWT.
    The request body is validated against the EventPayload model.
    """
    app_id = current_app.get("app_id")

    logger.info(f"Logging event for app_id={app_id}, type={event_payload.type}, source={event_payload.source}")

    event_data_string = json.dumps(event_payload.data, sort_keys=True)
    event_hash = hashlib.sha256(event_data_string.encode()).hexdigest()

    new_event = EventRecord(
        app_id=app_id,
        type=event_payload.type,
        source=event_payload.source,
        event_data=event_payload.data,
        event_hash=event_hash
    )
    try:
        event_dao.create(new_event)
    except ValueError as ve:
        logger.error(f"Event logging failed: {ve}")
        raise HTTPException(status_code=409, detail=str(ve))
    except Exception as e:
        logger.error(f"Event logging failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    logger.info(f"Event logged with hash={event_hash}")

    return {"status": "event logged successfully", "hash": event_hash}


@router.get("/events")
def get_events(current_app: dict = Depends(get_current_app)):
    """
    Retrieves all stored events for the authenticated application.
    """
    app_id = current_app.get("app_id")
    logger.info(f"Retrieving events for app_id={app_id}")
    events = event_dao.get_by_app_id(app_id=app_id)
    return events

def _verify_event_integrity(event: EventRecord) -> bool:
    """
    Recalculate the hash of the event's data and compare it to the stored hash.
    Returns True if the hashes match (not tampered), False otherwise.
    """
    event_data_string = json.dumps(event.event_data, sort_keys=True)
    recalculated_hash = hashlib.sha256(event_data_string.encode()).hexdigest()
    return recalculated_hash == event.event_hash

@router.get("/event/{event_id}/verify")
def verify_event_integrity(event_id: int, current_app: dict = Depends(get_current_app)):
    """
    Verifies the integrity of a specific event by comparing the stored hash with a recalculated hash.
    Only allows access to events belonging to the authenticated app.
    """
    app_id = current_app.get("app_id")
    event = event_dao.get_by_id(event_id)
    if not event:
        return {"status": "not found", "integrity": None, "message": "Event not found."}
    if event.app_id != app_id:
        return {"status": "forbidden", "integrity": None, "message": "You do not have access to this event."}
    is_valid = _verify_event_integrity(event)
    if is_valid:
        return {"status": "verified", "integrity": True}
    else:
        return {"status": "verification_failed", "integrity": False, "message": "This event may have been tampered with!"}
