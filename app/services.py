from vault.fetch_secrets import fetch_openai_key
import openai

# Fetch the OpenAI API key from Vault
openai.api_key = fetch_openai_key()

def process_command(command: str) -> dict:
    """Process user input using GPT-4."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a task management assistant."},
                {"role": "user", "content": command}
            ],
            max_tokens=150
        )
        # Simplified response parsing
        content = response['choices'][0]['message']['content']
        # Assuming content is structured as: {"description": "...", "due_date": "..."}
        return eval(content)  # Use a safer parser in production
    except Exception as e:
        print(f"Error processing command: {e}")
        return None
