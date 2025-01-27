from vault.fetch_secrets import fetch_openai_key
import openai
import logging
import json
import logging
from pydantic import ValidationError
from database_tools.schemas import TaskCreate

logging.basicConfig(level=logging.DEBUG)

# Fetch the OpenAI API key from Vault
print(fetch_openai_key())
openai.api_key = fetch_openai_key()

def process_command(command: str) -> dict:
    """Process user input using GPT-4 and handle both JSON and plain text."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a task management assistant. "
                        "Always respond in JSON format like this: "
                        "{'description': '...', 'due_date': '...'}. "
                        "If details are missing, include placeholders "
                        "or ask clarifying questions in the JSON."
                    )
                },
                {"role": "user", "content": command}
            ],
            max_tokens=100
        )
        logging.debug(f"API response: {response}")

        content = response['choices'][0]['message']['content']
        logging.debug(f"Extracted content: {content}")

        # Attempt to parse content as JSON
        try:
            parsed_content = json.loads(content)
            # Validate parsed JSON against TaskCreate
            validated_task = TaskCreate(**parsed_content)
            return validated_task.dict()
        except json.JSONDecodeError:
            logging.warning("Content is plain text. Handling as plain text.")
            # Treat plain text as description and leave due_date as None
            return {"description": content.strip(), "due_date": None}
        except ValidationError as e:
            logging.error(f"Validation error in JSON response: {e}")
            raise ValueError("Invalid response format from OpenAI.")
    except Exception as e:
        logging.error(f"Error processing command: {e}")
        return {"error": str(e)}