from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import generate_recurring_tasks
from database_tools.models import Task
from database_tools.schemas import TaskCreate, TaskResponse
from app.services import process_command, delete_root_token_after_process_start
from utils.background_tasks import process_task_in_background, get_task_status
from utils.scheduler import start_scheduler
from typing import List, Optional
from datetime import datetime

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
        priority=task_data.get("priority", 0),
        recurrence=task_data.get("recurrence"),
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # Generate recurring tasks if applicable
    if new_task.recurrence:
        generate_recurring_tasks(new_task, new_task.recurrence, db)

    # Send long-running tasks to Celery worker
    if "background" in task_data and task_data["background"]:
        process_task_in_background.delay(new_task.id)

    return new_task

# Endpoint: Retrieve all tasks with filters, pagination, and sorting
@app.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[int] = Query(None, description="Filter by task priority"),
    start_date: Optional[datetime] = Query(None, description="Filter tasks due after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter tasks due before this date"),
    page: int = Query(1, description="Page number"),
    page_size: int = Query(10, description="Number of tasks per page"),
    sort_by: Optional[str] = Query("due_date", description="Sort tasks by this field"),
    sort_order: Optional[str] = Query("asc", description="Sort order (asc or desc)"),
    ):
    """Retrieve all tasks with optional filters, pagination, and sorting."""
    query = db.query(Task).filter(Task.deleted_at == None)

    if status:
        query = query.filter(Task.status == status)
    if priority is not None:
        query = query.filter(Task.priority == priority)
    if start_date:
        query = query.filter(Task.due_date >= start_date)
    if end_date:
        query = query.filter(Task.due_date <= end_date)

    if hasattr(Task, sort_by):
        if sort_order == "desc":
            query = query.order_by(getattr(Task, sort_by).desc())
        else:
            query = query.order_by(getattr(Task, sort_by).asc())

    total_tasks = query.count()
    tasks = query.offset((page - 1) * page_size).limit(page_size).all()

    return tasks

# Endpoint: Retrieve a specific task by ID
@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """Retrieve a specific task by ID."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Endpoint: Update a task
@app.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task_update: TaskCreate, db: Session = Depends(get_db)):
    """Update an existing task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in task_update.dict(exclude_unset=True).items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task

# Endpoint: Delete a task
@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db)):
    """Soft - Delete a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.deleted_at = datetime.utcnow()
    db.commit()
    return {"detail": "Task marked as deleted."}

@app.post("/tasks", response_model=TaskResponse)
async def add_task(command: str, db: Session = Depends(get_db)):
    task_data = process_command(command)

    if not task_data or "error" in task_data:
        raise HTTPException(status_code=400, detail=task_data.get("error", "Invalid command"))

    new_task = Task(
        description=task_data["description"],
        due_date=task_data.get("due_date"),
        status="pending",
        priority=task_data.get("priority", 0),
        recurrence=task_data.get("recurrence"),
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    if new_task.recurrence:
        generate_recurring_tasks(new_task, new_task.recurrence, db)

    return new_task

# Endpoint: get status of backgroundtask...
@app.get("/tasks/{task_id}/status")
async def get_background_task_status(task_id: str, db: Session = Depends(get_db)):
    """
    Retrieve the status of a background task.
    Args:
        task_id (str): Celery task ID.

    Returns:
        dict: Task status and result.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} does not exist in the database.")

    try:
        status = get_task_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found.")
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/tasks/{task_id}/restore")
async def restore_task(task_id: str, db: Session = Depends(get_db)):
    """Restore a soft-deleted task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.deleted_at is None:
        raise HTTPException(status_code=400, detail="Task is not deleted, cannot restore")

    task.deleted_at = None
    db.commit()
    return {"message": f"Task {task_id} restored successfully"}
    
@app.on_event("startup")
async def startup_event():
    start_scheduler()