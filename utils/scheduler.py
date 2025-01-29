from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from database_tools.models import Task
import logging

logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler()

def send_reminder(task):
    """Simulate sending a reminder for a task."""
    logging.info(f"Reminder: Task '{task.description}' is due on {task.due_date}.")

def schedule_reminders():
    """Schedule reminders for all pending tasks."""
    db: Session = SessionLocal()
    try:
        now = datetime.now()
        tasks = db.query(Task).filter(
            Task.deleted_at == None,
            Task.status == "pending",
            Task.due_date > now,
            Task.due_date <= now + timedelta(days=1)  
        ).all()
        for task in tasks:
            scheduler.add_job(
                send_reminder,
                trigger="date",
                run_date=task.due_date - timedelta(minutes=30),  
                args=[task],
            )
    except Exception as e:
        logging.error(f"Error scheduling reminders: {e}")
    finally:
        db.close()

def start_scheduler():
    """Start the scheduler."""
    scheduler.add_job(schedule_reminders, "interval", minutes=30)  
    scheduler.start()
