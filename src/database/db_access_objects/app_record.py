from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class AppRecord:
    """Data class representing an app record."""
    id: Optional[int] = None
    name: str = ""
    api_key: str = ""
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @classmethod
    def from_record(cls, row):
        """Create an AppRecord instance from a database row."""
        return cls(
            id=row[0],
            name=row[1],
            api_key=row[2],
            created_at=row[3]
        ) 