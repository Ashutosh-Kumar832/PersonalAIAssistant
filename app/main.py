from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from database_tools.models import Task
from database_tools.schemas import TaskCreate, TaskResponse
from app.services import process_command, delete_root_token_after_process_start

app = FastAPI()

@app.post("/tasks", response_model=TaskResponse)
async def add_task(command: str, db: Session = Depends(get_db)):
    """Add a new task based on the given command."""
    task_data = process_command(command)
    
    # Now lets delete the root file.
    delete_root_token_after_process_start()

    if "error" in task_data:
        raise HTTPException(status_code=400, detail=task_data["error"])

    # Check if the response is plain text and return it as a message
    if "plain_text" in task_data:
        return {"message": task_data["plain_text"]}

    # Handle JSON response for task creation
    if not task_data.get("description"):
        raise HTTPException(status_code=400, detail="Invalid task details from the command.")

    new_task = Task(
        description=task_data["description"],
        due_date=task_data.get("due_date"),
        status="pending"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
