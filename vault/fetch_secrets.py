import hvac

# Vault server configuration
VAULT_URL = "http://127.0.0.1:8200"
VAULT_TOKEN = "root"

def fetch_openai_key():
    """Fetch the OpenAI API key from Vault."""
    client = hvac.Client(url=VAULT_URL, token=VAULT_TOKEN)
    if not client.is_authenticated():
        raise Exception("Vault authentication failed!")

    # Fetch the OpenAI API key from the Vault
    secret = client.secrets.kv.read_secret_version(path="secrets/openai")
    return secret["data"]["data"]["openai_key"]
