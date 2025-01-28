from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID  

class TaskResponse(BaseModel):
    id: UUID  
    description: str
    due_date: Optional[datetime] = None
    status: str
    priority: int

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    priority: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Complete the quarterly report",
                "due_date": "2025-02-01T10:00:00Z",
                "status": "pending",
                "priority": 1,
            }
        }
