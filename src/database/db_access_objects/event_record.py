from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class EventRecord:
    """Data class representing an event record."""
    id: Optional[int] = None
    app_id: int = 0
    type: str = ""
    source: Optional[str] = None
    event_data: Dict[str, Any] = None
    timestamp: datetime = None
    event_hash: str = ""
    auth_signature: Optional[str] = None
    
    def __post_init__(self):
        if self.event_data is None:
            self.event_data = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @classmethod
    def from_record(cls, row):
        """Create an EventRecord instance from a database row."""
        return cls(
            id=row[0],
            app_id=row[1],
            type=row[2],
            source=row[3],
            event_data=row[4],
            timestamp=row[5],
            event_hash=row[6],
            auth_signature=row[7]
        )
