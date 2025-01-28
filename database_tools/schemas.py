from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal
from uuid import UUID  

class TaskResponse(BaseModel):
    id: UUID  
    description: str
    due_date: Optional[datetime] = None
    status: str
    priority: int
    recurrence: Optional[str] = None
    celery_task_id: Optional[str] = None

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    recurrence: Optional[Literal["daily", "weekly", "monthly"]] = Field(
        None, description="Recurrence type: daily, weekly, or monthly"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Complete the quarterly report",
                "due_date": "2025-02-01T10:00:00Z",
                "status": "pending",
                "priority": 1,
                "recurrence": "weekly",
            }
        }
