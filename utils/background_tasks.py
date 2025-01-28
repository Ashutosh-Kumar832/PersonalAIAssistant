import os
import time
from celery import Celery
from sqlalchemy.orm import Session
from app.database import SessionLocal
from database_tools.models import Task

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "background_tasks",
    broker=redis_url,
    backend=redis_url
)

@celery_app.task
def process_task_in_background(task_id: str):
    """Process a task in the background."""
    session = SessionLocal()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")
        task.status = "in progress"
        session.commit()
        time.sleep(10)  # Simulate processing
        task.status = "completed"
        session.commit()
    except Exception as e:
        print(f"Error processing task {task_id}: {e}")
    finally:
        session.close()