from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
    command: str

class TaskResponse(BaseModel):
    id: str
    description: str
    due_date: Optional[datetime] = None
    status: str

    class Config:
        orm_mode = True
