from typing import List, Optional
import json
from ..db_service import get_db
from .event_record import EventRecord

class EventDAO:
    """Data Access Object for event operations using plain SQL queries."""
    
    def __init__(self):
        self.table_name = "events"
        self.return_columns = "id, app_id, type, source, event_data, timestamp, event_hash, auth_signature"
    
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
            auth_signature VARCHAR(256)
        );
        """
        
        with get_db() as (_, cur):
            cur.execute(create_table_sql)
    
    def create(self, event: EventRecord) -> EventRecord:
        """Create a new event record."""
        insert_sql = f"""
        INSERT INTO events (app_id, type, source, event_data, timestamp, event_hash, auth_signature)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING {self.return_columns};
        """
        
        with get_db() as (_, cur):
            cur.execute(insert_sql, (
                event.app_id,
                event.type,
                event.source,
                json.dumps(event.event_data),
                event.timestamp,
                event.event_hash,
                event.auth_signature
            ))
            
            result = cur.fetchone()
            return EventRecord.from_record(result)
    
    def get_by_id(self, event_id: int) -> Optional[EventRecord]:
        """Get an event by its ID."""
        select_sql = f"""
        SELECT {self.return_columns}
        FROM events
        WHERE id = %s;
        """
        
        with get_db() as (_, cur):
            cur.execute(select_sql, (event_id,))
            result = cur.fetchone()
            
            return EventRecord.from_record(result) if result else None
    
    def get_all(self) -> List[EventRecord]:
        """Get all events."""
        select_sql = f"""
        SELECT {self.return_columns}
        FROM events
        ORDER BY timestamp DESC;
        """
        
        with get_db() as (_, cur):
            cur.execute(select_sql)
            results = cur.fetchall()
            
            return [EventRecord.from_record(row) for row in results]
    
    def update(self, event: EventRecord) -> Optional[EventRecord]:
        """Update an existing event."""
        update_sql = f"""
        UPDATE events
        SET app_id = %s, type = %s, source = %s, event_data = %s, timestamp = %s, event_hash = %s, auth_signature = %s
        WHERE id = %s
        RETURNING {self.return_columns};
        """
        
        with get_db() as (_, cur):
            cur.execute(update_sql, (
                event.app_id,
                event.type,
                event.source,
                json.dumps(event.event_data),
                event.timestamp,
                event.event_hash,
                event.auth_signature,
                event.id
            ))
            
            result = cur.fetchone()
            return EventRecord.from_record(result) if result else None
    
    def delete(self, event_id: int) -> bool:
        """Delete an event by its ID."""
        delete_sql = """
        DELETE FROM events
        WHERE id = %s;
        """
        
        with get_db() as (_, cur):
            cur.execute(delete_sql, (event_id,))
            return cur.rowcount > 0
