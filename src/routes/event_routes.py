# src/routes/event_routes.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import hashlib
import json

# Import the dependency and DAOs
from src.security import get_current_app
from src.database.db_access_objects.event_dao import EventDAO
from src.database.db_access_objects.event_record import EventRecord

router = APIRouter()
event_dao = EventDAO()

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

    event_data_string = json.dumps(event_payload.data, sort_keys=True)
    event_hash = hashlib.sha256(event_data_string.encode()).hexdigest()

    new_event = EventRecord(
        app_id=app_id,
        type=event_payload.type,
        source=event_payload.source,
        event_data=event_payload.data,
        event_hash=event_hash
    )
    event_dao.create(new_event)

    return {"status": "event logged successfully", "hash": event_hash}


@router.get("/events")
def get_events(current_app: dict = Depends(get_current_app)):
    """
    Retrieves all stored events for the authenticated application.
    """
    app_id = current_app.get("app_id")
    events = event_dao.get_all_for_app(app_id=app_id)
    return events
