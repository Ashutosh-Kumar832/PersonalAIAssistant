from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from database_tools.models import Task
from database_tools.schemas import TaskCreate, TaskResponse
from app.services import process_command

app = FastAPI()

@app.post("/tasks", response_model=TaskResponse)
async def add_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Add a new task."""
    task_data = process_command(task.command)
    if not task_data:
        raise HTTPException(status_code=400, detail="Invalid command.")

    new_task = Task(
        description=task_data["description"],
        due_date=task_data.get("due_date"),
        status="pending"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
