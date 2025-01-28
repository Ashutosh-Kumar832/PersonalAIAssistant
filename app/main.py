from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from database_tools.models import Task
from database_tools.schemas import TaskCreate, TaskResponse
from app.services import process_command, delete_root_token_after_process_start
from utils.background_tasks import process_task_in_background

app = FastAPI()

@app.post("/tasks", response_model=TaskResponse)
async def add_task(command: str, db: Session = Depends(get_db)):
    """Add a new task based on the given command."""
    # Parse the command to extract task data
    task_data = process_command(command)

    # Now let's delete the root token for security
    #delete_root_token_after_process_start()

    if not task_data or "error" in task_data:
        raise HTTPException(status_code=400, detail=task_data.get("error", "Invalid command"))

    # Handle plain text responses
    if "plain_text" in task_data:
        return {"message": task_data["plain_text"]}

    # Ensure the task data has a description
    if not task_data.get("description"):
        raise HTTPException(status_code=400, detail="Task description is required.")

    # Create a new task in the database
    new_task = Task(
        description=task_data["description"],
        due_date=task_data.get("due_date"),
        status="pending",
        priority=task_data.get("priority", 0),  # Default priority to 0
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Send long-running tasks to Celery worker
    if "background" in task_data and task_data["background"]:
        process_task_in_background.delay(new_task.id)

    return new_task
