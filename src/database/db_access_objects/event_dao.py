from typing import List, Optional
import json
from ..db_service import get_db
from .event_record import EventRecord
from src.logger import get_logger
import psycopg2.errors

logger = get_logger(__name__)

class EventDAO:
    """Data Access Object for event operations using plain SQL queries."""
    
    def __init__(self):
        self.table_name = "events"
        self.return_columns = "id, app_id, type, source, event_data, timestamp, event_hash, prev_event_hash"
    
    def create_table(self) -> None:
        """Create the events table if it doesn't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL PRIMARY KEY,
            app_id INT NOT NULL REFERENCES apps(id),
            type VARCHAR(64) NOT NULL,
            source VARCHAR(128),
            event_data JSONB NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            event_hash VARCHAR(128) NOT NULL,
            prev_event_hash VARCHAR(128)
        );
        """
        logger.info("Creating events table if not exists.")
        with get_db() as (_, cur):
            cur.execute(create_table_sql)
    
    def create(self, event: EventRecord) -> EventRecord:
        """Create a new event record."""
        insert_sql = f"""
        INSERT INTO events (app_id, type, source, event_data, timestamp, event_hash, prev_event_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING {self.return_columns};
        """
        logger.info(f"Creating event for app_id={event.app_id}, type={event.type}")
        try:
            with get_db() as (_, cur):
                cur.execute(insert_sql, (
                    event.app_id,
                    event.type,
                    event.source,
                    json.dumps(event.event_data),
                    event.timestamp,
                    event.event_hash,
                    event.prev_event_hash
                ))
                result = cur.fetchone()
                logger.info(f"Event created with id={result[0] if result else 'unknown'}")
                return EventRecord.from_record(result)
        except psycopg2.errors.UniqueViolation:
            logger.error(f"Event creation failed: Duplicate event for app_id={event.app_id} and hash={event.event_hash}.")
            raise ValueError("Duplicate event detected for this app.")
    
    def get_by_id(self, event_id: int) -> Optional[EventRecord]:
        """Get an event by its ID."""
        select_sql = f"""
        SELECT {self.return_columns}
        FROM events
        WHERE id = %s;
        """
        logger.info(f"Fetching event by id={event_id}")
        with get_db() as (_, cur):
            cur.execute(select_sql, (event_id,))
            result = cur.fetchone()
            
            return EventRecord.from_record(result) if result else None
    
    def get_by_app_id(self, app_id: int) -> List[EventRecord]:
        """Get all events for a given app_id."""
        select_sql = f"""
        SELECT {self.return_columns}
        FROM events
        WHERE app_id = %s
        ORDER BY timestamp DESC;
        """
        logger.info(f"Fetching events for app_id={app_id}")
        with get_db() as (_, cur):
            cur.execute(select_sql, (app_id,))
            results = cur.fetchall()
            
            return [EventRecord.from_record(row) for row in results]
    
    def update(self, event: EventRecord) -> Optional[EventRecord]:
        """Update an existing event."""
        update_sql = f"""
        UPDATE events
        SET app_id = %s, type = %s, source = %s, event_data = %s, timestamp = %s, event_hash = %s, prev_event_hash = %s
        WHERE id = %s
        RETURNING {self.return_columns};
        """
        logger.info(f"Updating event id={event.id}")
        try:
            with get_db() as (_, cur):
                cur.execute(update_sql, (
                    event.app_id,
                    event.type,
                    event.source,
                    json.dumps(event.event_data),
                    event.timestamp,
                    event.event_hash,
                    event.prev_event_hash,
                    event.id
                ))
                result = cur.fetchone()
                return EventRecord.from_record(result) if result else None
        except psycopg2.errors.UniqueViolation:
            logger.error(f"Event update failed: Duplicate event for app_id={event.app_id} and hash={event.event_hash}.")
            raise ValueError("Duplicate event detected for this app.")
    
    def delete(self, event_id: int) -> bool:
        """Delete an event by its ID."""
        delete_sql = """
        DELETE FROM events
        WHERE id = %s;
        """
        logger.info(f"Deleting event id={event_id}")
        with get_db() as (_, cur):
            cur.execute(delete_sql, (event_id,))
            return cur.rowcount > 0

    def get_latest_by_app_id(self, app_id: int, for_update: bool = False) -> Optional[EventRecord]:
        """Get the latest event for a given app_id, optionally locking the row for update."""
        select_sql = f"""
        SELECT {self.return_columns}
        FROM events
        WHERE app_id = %s
        ORDER BY timestamp DESC, id DESC
        LIMIT 1
        {"FOR UPDATE" if for_update else ""};
        """
        logger.info(f"Fetching latest event for app_id={app_id} with lock={for_update}")
        with get_db() as (conn, cur):
            cur.execute(select_sql, (app_id,))
            result = cur.fetchone()
            return EventRecord.from_record(result) if result else None
