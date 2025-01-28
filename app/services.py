from vault.fetch_secrets import fetch_openai_key, TOKEN_FILE
import openai
import logging
import json
import os
import parsedatetime
from pydantic import ValidationError
from database_tools.schemas import TaskCreate
from database_tools.models import Task
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
from sqlalchemy.orm import Session


logging.basicConfig(level=logging.DEBUG)

# Fetch the OpenAI API key from Vault
openai.api_key = fetch_openai_key()

def delete_root_token_after_process_start():
    """Delete Vault's root token after startup for security."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        logging.debug("Root token file deleted for security.")

def parse_natural_language_date(date_str: str) -> str:
    """
    Convert a natural language date into ISO 8601 format.

    Args:
        date_str (str): A natural language date (e.g., "next Friday").

    Returns:
        str: ISO 8601 formatted date or None if parsing fails.
    """
    cal = parsedatetime.Calendar()
    time_struct, parse_status = cal.parse(date_str)
    
    if parse_status == 1: 
        parsed_date = datetime(*time_struct[:6])
        # Check if the parsed date is in the past and adjust if necessary
        if parsed_date < datetime.now():
            logging.warning(f"Parsed date {parsed_date} is in the past. Adjusting...")
            parsed_date += timedelta(days=7)  # Add a week to ensure a future date
        return parsed_date.isoformat()
    
    logging.warning(f"Could not parse due_date: {date_str}")
    return None

def fallback_parse_command(command: str) -> dict:
    """
    A fallback parser to extract details if GPT fails.

    Args:
        command (str): The user's command.

    Returns:
        dict: Extracted task details.
    """
    try:
        parts = command.split(",")
        description = parts[0].strip()
        due_date = None
        recurrence = None

        # Parse due_date from the command
        for part in parts:
            if "on" in part or "by" in part:
                due_date = parse_natural_language_date(part.strip())
            elif any(freq in part for freq in ["daily", "weekly", "monthly"]):
                recurrence = part.strip().lower()

        return {
            "description": description,
            "due_date": due_date,
            "recurrence": recurrence,
        }
    except Exception as e:
        logging.error(f"Fallback parsing failed: {e}")
        return {}

def process_command(command: str) -> dict:
    """Process user input using GPT and handle JSON/validation errors."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a task management assistant. "
                        "Always respond in JSON format like this: "
                        '{"description": "...", "due_date": "...", "background": true/false, "recurrence": "daily/weekly/monthly"}. '
                        "Ensure valid JSON in your responses. If information is missing, suggest fixes."
                    ),
                },
                {"role": "user", "content": command},
            ],
            max_tokens=100,
        )

        logging.debug(f"Raw OpenAI Response: {response}")
        content = response["choices"][0]["message"]["content"]

        # Parse content as JSON
        parsed_content = json.loads(content)
        logging.debug(f"Parsed JSON Content: {parsed_content}")

        # Convert natural language dates to ISO format
        if "due_date" in parsed_content and parsed_content["due_date"]:
            parsed_content["due_date"] = parse_natural_language_date(parsed_content["due_date"])

        # Validate using TaskCreate schema
        validated_task = TaskCreate(**parsed_content)
        
        # Additional validation for recurrence (already handled by schema)
        if validated_task.recurrence and validated_task.recurrence not in ["daily", "weekly", "monthly"]:
            raise ValueError(f"Invalid recurrence value: {validated_task.recurrence}")

        return validated_task.dict()

    except json.JSONDecodeError:
        logging.error("Invalid JSON format received. Falling back to plain text response.")
        return fallback_parse_command()
    except ValidationError as e:
        logging.error(f"Validation error: {e}")
        missing_fields = [error['loc'][0] for error in e.errors()]
        suggestions = suggest_missing_fields(parsed_content)

        return {
            "error": "Validation failed.",
            "missing_fields": missing_fields,
            "suggestions": suggestions,
            "message": "Please provide the missing details."
        }
    except Exception as e:
        logging.error(f"Unexpected error while processing command: {e}")
        return {"error": str(e)}
    
def generate_recurring_tasks(task: Task, recurrence: str, db: Session, occurrences: int = 10):
    """Generate recurring tasks based on recurrence."""
    rules = {
        "daily": DAILY,
        "weekly": WEEKLY,
        "monthly": MONTHLY,
    }
    if recurrence not in rules:
        raise ValueError(f"Unsupported recurrence: {recurrence}")
    dates = list(rrule(rules[recurrence], dtstart=task.due_date, count=occurrences))
    for date in dates[1:]:  
        new_task = Task(
            description=task.description,
            due_date=date,
            status=task.status,
            priority=task.priority,
            recurrence=task.recurrence,
        )
        db.add(new_task)
    db.commit()
    
def suggest_missing_fields(parsed_content: dict) -> dict:
    """Suggest fixes for missing fields."""
    suggestions = {}
    if not parsed_content.get("description"):
        suggestions["description"] = "What should the task be about?"
    if not parsed_content.get("due_date"):
        suggestions["due_date"] = "When is the deadline? (e.g., tomorrow, next week)"
    if not parsed_content.get("recurrence"):
        suggestions["recurrence"] = "Is this a recurring task? (daily, weekly, monthly)"

    return suggestions

