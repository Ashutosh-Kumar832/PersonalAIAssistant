import hvac
import os

# Vault server configuration
VAULT_URL = "http://127.0.0.1:8200"

def get_root_token():
    """Retrieve the root token from the saved file."""
    token_file = os.path.join(os.path.dirname(__file__), "root_token.txt")
    try:
        with open(token_file, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        raise Exception("Root token file not found. Start the Vault server first.")

def fetch_openai_key():
    """Fetch the OpenAI API key from Vault."""
    vault_token = get_root_token()
    client = hvac.Client(url=VAULT_URL, token=vault_token)
    if not client.is_authenticated():
        raise Exception("Vault authentication failed!")

    # Fetch the OpenAI API key from the Vault
    secret = client.secrets.kv.read_secret_version(path="openai")  
    api_key = secret["data"]["data"]["api_key"]
    print(f"Fetched API key: {api_key}")
    return api_key
