import os
import sys
import subprocess
import platform
import shutil


def check_python_version():
    """Check if Python is installed and meets the version requirement."""
    python_version = sys.version_info
    if python_version < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    print(f"Python version: {platform.python_version()} is compatible.")


def install_requirements():
    """Install Python dependencies."""
    if not shutil.which("pip"):
        print("Error: pip is not installed.")
        sys.exit(1)

    print("Installing dependencies from requirements.txt...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)


def check_postgres():
    """Check if PostgreSQL is installed."""
    if platform.system() == "Windows":
        postgres_command = "psql --version"
    else:
        postgres_command = "which psql"

    result = subprocess.run(postgres_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        print("PostgreSQL is already installed.")
    else:
        print("Error: PostgreSQL is not installed. Please install PostgreSQL before proceeding.")
        sys.exit(1)


def setup_vault():
    """Set up Vault and prompt the user for the OpenAI API key."""
    print("Starting Vault setup...")
    vault_script = "./vault/run_vault.sh"
    if not os.path.exists(vault_script):
        print("Error: Vault script not found.")
        sys.exit(1)

    print("Starting Vault server...")
    subprocess.Popen([vault_script])

    print("Please enter your OpenAI API key:")
    api_key = input("> ").strip()
    if not api_key:
        print("Error: API key cannot be empty.")
        sys.exit(1)

    print("Storing API key in Vault...")
    subprocess.run(["./vault/set_secrets.sh"], input=f"{api_key}\n", text=True, check=True)
    print("OpenAI API key stored successfully in Vault.")


def start_application():
    """Start the FastAPI application."""
    print("Starting the FastAPI application...")
    subprocess.Popen(["uvicorn", "app.main:app", "--reload", "--port", "8000"])
    print("Application is running on http://127.0.0.1:8000")


def main():
    print("Initializing setup...")

    # Step 1: Check Python version
    check_python_version()

    # Step 2: Install Python dependencies
    install_requirements()

    # Step 3: Check for PostgreSQL installation
    check_postgres()

    # Step 4: Set up Vault and store the OpenAI API key
    setup_vault()

    # Step 5: Start the FastAPI application
    start_application()

    print("Setup complete. Both Vault and the application are running on separate ports.")


if __name__ == "__main__":
    main()
