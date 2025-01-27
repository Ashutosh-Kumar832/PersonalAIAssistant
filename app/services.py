from vault.fetch_secrets import fetch_openai_key
import openai
import logging
import json

logging.basicConfig(level=logging.DEBUG)

# Fetch the OpenAI API key from Vault
print(fetch_openai_key())
openai.api_key = fetch_openai_key()

def process_command(command: str) -> dict:
    """Process user input using GPT-4."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a task management assistant."},
                {"role": "user", "content": command}
            ],
            max_tokens=50
        )
        logging.debug(f"API response: {response}")

        # Extract the content field
        content = response['choices'][0]['message']['content']
        logging.debug(f"Extracted content: {content}")

        # Try parsing the content as JSON
        try:
            parsed_content = json.loads(content)
            logging.debug(f"Parsed JSON content: {parsed_content}")
            return parsed_content
        except json.JSONDecodeError:
            logging.warning("Content is not valid JSON. Returning plain text.")
            return {"description": content.strip(), "due_date": None}

    except Exception as e:
        logging.error(f"Error processing command: {e}")
        return {"error": str(e)}