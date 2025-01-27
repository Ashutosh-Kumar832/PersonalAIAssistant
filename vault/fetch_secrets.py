import os
import hvac

VAULT_URL = "http://127.0.0.1:8200"
TOKEN_FILE = os.path.join("vault", "root_token.txt")


def get_root_token():  # sourcery skip: raise-from-previous-error
    """Retrieve the root token from the file."""
    try:
        with open(TOKEN_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        raise FileNotFoundException(f"Root token file not found at {TOKEN_FILE}. Start the Vault server first.")


def fetch_openai_key():  # sourcery skip: inline-immediately-returned-variable
    """Fetch the OpenAI API key from Vault."""
    vault_token = get_root_token()
    client = hvac.Client(url=VAULT_URL, token=vault_token)
    if not client.is_authenticated():
        raise FetchOpenAIKeyException("Vault authentication failed!")

    # Fetch the OpenAI API key
    secret = client.secrets.kv.read_secret_version(path="openai")
    api_key = secret["data"]["data"]["api_key"]
    return api_key

class FileNotFoundException(Exception):
    pass
class FetchOpenAIKeyException(Exception):
    pass
