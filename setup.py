import os
import sys
import platform
import shutil
import socket
import subprocess
import psutil
import time


def check_python_version():
    """Check if Python is installed and meets the version requirement."""
    python_version = sys.version_info
    if python_version < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    print(f"Python version: {platform.python_version()} is compatible.")


def stop_process_on_port(port):
    """
    Check if a port is in use and stop the process using it.
    """
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
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("Error installing dependencies. Check your requirements.txt.")
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


def setup_vault(api_key):
    """Set up Vault and store the OpenAI API key."""
    print("Starting Vault setup...")
    vault_process = subprocess.Popen(
        ["vault", "server", "-dev"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        # Wait for Vault to initialize
        print("Waiting for Vault to initialize...")
        time.sleep(5)

        print("Storing API key in Vault...")
        subprocess.run(
            ["vault", "kv", "put", "secret/openai", f"api_key={api_key}"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("API key stored in Vault successfully.")
    except subprocess.CalledProcessError:
        print("Error storing API key in Vault. Ensure the Vault server is running.")
        sys.exit(1)
    finally:
        vault_process.terminate()


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
    install_vault()  
    install_postgres()  
    setup_vault(api_key)  

    print("Setup complete. Vault and PostgreSQL are ready to use.")


if __name__ == "__main__":
    main()
