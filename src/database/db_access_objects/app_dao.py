# src/database/db_access_objects/app_dao.py

import uuid
from typing import List, Optional
from ..db_service import get_db
from .app_record import AppRecord

class AppDAO:
    """Data Access Object for app operations using plain SQL queries."""
    
    def __init__(self):
        self.table_name = "apps"
        self.return_columns = "id, name, api_key, created_at"
    
    def create_table(self) -> None:
        """Create the apps table if it doesn't exist."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS apps (
            id SERIAL PRIMARY KEY,
            name VARCHAR(128) NOT NULL UNIQUE,
            api_key TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        
        with get_db() as (_, cur):
            cur.execute(create_table_sql)
    
    def create(self, app: AppRecord) -> AppRecord:
        """Create a new app record."""
        insert_sql = f"""
        INSERT INTO apps (name, api_key, created_at)
        VALUES (%s, %s, %s)
        RETURNING {self.return_columns};
        """
        
        with get_db() as (_, cur):
            cur.execute(insert_sql, (
                app.name,
                app.api_key,
                app.created_at
            ))
            
            result = cur.fetchone()
            return AppRecord.from_record(result)
    
    def get_by_id(self, app_id: int) -> Optional[AppRecord]:
        """Get an app by its ID."""
        select_sql = f"""
        SELECT {self.return_columns}
        FROM apps
        WHERE id = %s;
        """
        
        with get_db() as (_, cur):
            cur.execute(select_sql, (app_id,))
            result = cur.fetchone()
            
            return AppRecord.from_record(result) if result else None
    
    def get_by_name(self, name: str) -> Optional[AppRecord]:
        """Get an app by its name."""
        select_sql = f"""
        SELECT {self.return_columns}
        FROM apps
        WHERE name = %s;
        """
        
        with get_db() as (_, cur):
            cur.execute(select_sql, (name,))
            result = cur.fetchone()
            
            return AppRecord.from_record(result) if result else None
    
    def get_all(self) -> List[AppRecord]:
        """Get all apps."""
        select_sql = f"""
        SELECT {self.return_columns}
        FROM apps
        ORDER BY created_at DESC;
        """
        
        with get_db() as (_, cur):
            cur.execute(select_sql)
            results = cur.fetchall()
            
            return [AppRecord.from_record(row) for row in results]
    
    def update(self, app: AppRecord) -> Optional[AppRecord]:
        """Update an existing app."""
        update_sql = f"""
        UPDATE apps
        SET name = %s, api_key = %s
        WHERE id = %s
        RETURNING {self.return_columns};
        """
        
        with get_db() as (_, cur):
            cur.execute(update_sql, (
                app.name,
                app.api_key,
                app.id
            ))
            
            result = cur.fetchone()
            return AppRecord.from_record(result) if result else None
    
    def delete(self, app_id: int) -> bool:
        """Delete an app by its ID."""
        delete_sql = """
        DELETE FROM apps
        WHERE id = %s;
        """
        
        with get_db() as (_, cur):
            cur.execute(delete_sql, (app_id,))
            return cur.rowcount > 0