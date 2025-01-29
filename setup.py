import os
import sys
import platform
import shutil
import socket
import subprocess
import psutil


def check_python_version():
    """Check if Python is installed and meets the version requirement."""
    python_version = sys.version_info
    if python_version < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    print(f"Python version: {platform.python_version()} is compatible.")


def stop_process_on_port(port):
    """Check if a port is in use and stop the process using it."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) == 0:
                print(f"Port {port} is in use. Attempting to stop the process...")
                for proc in psutil.process_iter(attrs=["pid", "name"]):
                    try:
                        for conn in proc.connections(kind="inet"):
                            if conn.laddr.port == port:
                                print(f"Stopping process '{proc.info['name']}' (PID {proc.info['pid']}) on port {port}...")
                                proc.terminate()
                                proc.wait(timeout=5)
                                print(f"Process on port {port} stopped successfully.")
                                return True
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        continue
    except Exception as e:
        print(f"Error stopping process on port {port}: {e}")
    return False


def install_requirements():
    """Install Python dependencies."""
    print("Installing dependencies from requirements.txt...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("Error installing dependencies. Check your requirements.txt.")
        sys.exit(1)

def run_redis_setup():
    """Run the Redis installation and setup script."""
    print("Setting up Redis...")
    redis_setup_script = "./install_redis.sh"
    if not os.path.exists(redis_setup_script):
        print(f"Error: {redis_setup_script} script not found.")
        sys.exit(1)

    if not os.access(redis_setup_script, os.X_OK):
        os.chmod(redis_setup_script, 0o755)

    try:
        subprocess.run(["bash", redis_setup_script], check=True)
        print("Redis setup completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Redis setup: {e}")
        sys.exit(1)

def start_redis():
    """Start Redis server."""
    print("Checking for Redis installation...")
    redis_path = shutil.which("redis-server")

    if not redis_path:
        print("Error: Redis is not installed. Please install Redis and try again.")
        sys.exit(1)

    print("Starting Redis server...")
    try:
        subprocess.Popen(["redis-server"])
        print("Redis server started successfully on port 6379.")
    except Exception as e:
        print(f"Error starting Redis server: {e}")
        sys.exit(1)
        
def start_celery_worker():
    """Start the Celery worker."""
    try:
        print("Starting the Celery worker...")
        subprocess.Popen(
            ["celery", "-A", "utils.background_tasks.celery_app", "worker", "--loglevel=info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Celery worker started successfully.")
    except Exception as e:
        print(f"Error starting Celery worker: {e}")
        sys.exit(1)

def install_vault():
    """Check if Vault is installed and install if necessary."""
    print("Checking for Vault installation...")
    if shutil.which("vault"):
        print("Vault is already installed.")
        return

    print("Vault is not installed. Attempting to install...")
    os_name = platform.system()

    try:
        if os_name == "Darwin":
            subprocess.run(["brew", "install", "vault"], check=True)
        elif os_name == "Linux":
            subprocess.run([
                "curl", "-fsSL",
                "https://releases.hashicorp.com/vault/1.13.4/vault_1.13.4_linux_amd64.zip",
                "-o", "vault.zip"
            ], check=True)
            subprocess.run(["unzip", "vault.zip", "-d", "/usr/local/bin"], check=True)
            os.remove("vault.zip")
        else:
            print("Vault installation is not supported on this OS.")
            sys.exit(1)
        print("Vault installed successfully.")
    except subprocess.CalledProcessError:
        print("Error installing Vault. Please install it manually.")
        sys.exit(1)
        
def persist_root_token(root_token):
    """Save the Vault root token to a file."""
    token_file = os.path.join("config", "root_token.txt")
    os.makedirs(os.path.dirname(token_file), exist_ok=True)
    with open(token_file, "w") as file:
        file.write(root_token)
    print(f"Root token saved to {token_file}")
    
def start_vault_and_get_root_token():
    """Start the Vault server and capture the root token."""
    print("Starting Vault server...")
    vault_process = subprocess.Popen(
        ["vault", "server", "-dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    root_token = None
    while True:
        line = vault_process.stdout.readline()
        if "Root Token:" in line:
            root_token = line.split("Root Token:")[1].strip()
            print(f"Captured Root Token: {root_token}")
            break

        if vault_process.poll() is not None:
            raise VaultException("Vault server failed to start.")

    return root_token

def store_api_key_in_vault(root_token, api_key):
    """Store the OpenAI API key in Vault using the root token."""
    os.environ["VAULT_ADDR"] = "http://127.0.0.1:8200"
    os.environ["VAULT_TOKEN"] = root_token

    try:
        # Create a policy for accessing the API key
        policy = """
        path "secret/data/openai" {
          capabilities = ["read", "create", "update"]
        }
        """
        with open("openai-policy.hcl", "w") as f:
            f.write(policy)

        subprocess.run(["vault", "policy", "write", "openai-policy", "openai-policy.hcl"], check=True)
        os.remove("openai-policy.hcl")

        # Store the API key in Vault
        subprocess.run(["vault", "kv", "put", "secret/openai", f"api_key={api_key}"], check=True)
        print("API key stored in Vault successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error storing API key in Vault: {e}")
        sys.exit(1)


def install_postgres():
    """Run the PostgreSQL installation script."""
    print("Checking and installing PostgreSQL if necessary...")
    postgres_script = "./install_postgres.sh"
    if not os.path.exists(postgres_script):
        print(f"Error: {postgres_script} script not found.")
        sys.exit(1)

    if not os.access(postgres_script, os.X_OK):
        os.chmod(postgres_script, 0o755)

    subprocess.run(["bash", postgres_script], check=True)
    print("PostgreSQL setup complete.")

def run_database_setup():
    """Run the database_tools/setup_database.py script to initialize the database."""
    print("Setting up the database...")
    database_setup_script = os.path.join("database_tools", "setup_database.py")
    if not os.path.exists(database_setup_script):
        print(f"Error: {database_setup_script} script not found.")
        sys.exit(1)

    try:
        subprocess.run(
            [sys.executable, database_setup_script],
            check=True
        )
        print("Database setup completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running database setup: {e}")
        sys.exit(1)

def start_application():
    """Start the FastAPI application."""
    try:
        print("Starting the FastAPI application...")
        subprocess.Popen(
            ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        )
        print("FastAPI application started at http://127.0.0.1:8000")
    except Exception as e:
        print(f"Error starting FastAPI application: {e}")
        sys.exit(1)


def main():
    print("Initializing setup...")

    check_python_version()
    install_requirements()

    print("Please enter your OpenAI API key:")
    api_key = input("> ").strip()
    while not api_key:
        print("API key cannot be empty. Please enter a valid OpenAI API key:")
        api_key = input("> ").strip()

    stop_process_on_port(8200)
    stop_process_on_port(8000)
    stop_process_on_port(6379)  

    install_vault()
    root_token = start_vault_and_get_root_token()
    persist_root_token(root_token)
    store_api_key_in_vault(root_token, api_key)

    run_redis_setup()
    start_redis()
    install_postgres()
    run_database_setup()
    start_application()
    start_celery_worker()

    print("Setup complete. Vault, Redis, and PostgreSQL are ready to use.")

if __name__ == "__main__":
    main()
    
    
class VaultException(Exception):
    pass