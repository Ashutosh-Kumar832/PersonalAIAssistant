from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID  # Import UUID type

class TaskResponse(BaseModel):
    id: UUID  # Change from str to UUID
    description: str
    due_date: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True  # Correct the config for Pydantic v2

class TaskCreate(BaseModel):
    description: str
    due_date: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "description": "Complete the project",
                "due_date": "2025-01-27T21:22:48.077Z"
            }
        }
