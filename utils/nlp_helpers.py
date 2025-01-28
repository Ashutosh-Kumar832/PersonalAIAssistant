from datetime import datetime
import re

def parse_command(command: str) -> dict:
    """
    Parse a natural language command into structured data.

    Args:
        command (str): The user's command.

    Returns:
        dict: Extracted description, due_date, and other fields.
    """
    # parsing logic for due dates
    date_patterns = [
        r"(on|by)\s+(\d{4}-\d{2}-\d{2})",  # Match YYYY-MM-DD
        r"(on|by)\s+(\w+\s\d{1,2}(?:st|nd|rd|th)?)"  # Match natural dates
    ]
    due_date = None
    for pattern in date_patterns:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            try:
                due_date = datetime.strptime(match.group(2), "%Y-%m-%d")
                break
            except ValueError:
                # Handle natural language dates
                pass

    # Extract description
    description = re.sub(r"(on|by)\s+\S+", "", command).strip()
    return {
        "description": description,
        "due_date": due_date.isoformat() if due_date else None
    }
