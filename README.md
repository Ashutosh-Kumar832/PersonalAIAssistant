# Personal Task Manager Assistant

This project provides a personal task management assistant powered by **FastAPI**, **PostgreSQL**, **HashiCorp Vault**, and **OpenAI GPT models**. It works seamlessly on macOS, Linux, and Windows.

---

## Quick Start

### Prerequisites

1. **Python 3.8 or higher** ([Download Python](#https://www.python.org/downloads/)).
2. **Vault** installed (Windows users only—see [Installing Vault on Windows](#installing-vault-on-windows)).
3. An **OpenAI API key** (see [Getting Your OpenAI API Key](#getting-your-openai-api-key)).

---

### How to Run

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Ashutosh-Kumar832/PersonalAIAssistant/tree/main
   cd PersonalAIAssistant

2. **Run the Setup Script**

    To set up and run the application:

    ```bash
    python3 setup.py (linux/ macOS).
    python setup.py (Windows).

# What the Script Will Do

1. Install required Python dependencies.
2. Install and configure **Vault** (on macOS/Linux).
3. Start Vault in dev mode.
4. Prompt you to input your **OpenAI API key** and securely store it in Vault.
5. Set up **PostgreSQL** and initialize the database.
6. Start the **FastAPI** application at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Additional Steps for Windows Users

### Installing Python

1. Download the installer for Python 3.8+ from [python.org](https://www.python.org/).
2. During installation, check the **Add Python to PATH** option.

### Installing Vault

1. Download the Windows Vault binary from the [official HashiCorp Vault releases page](https://www.vaultproject.io/downloads).
2. Extract the binary and add its location to your system's **PATH**.

### Updating PostgreSQL Credentials

1. Open the file: `database_tools/setup_database.py`.
2. Modify the following lines:

    ```python
    ADMIN_USER = "postgres"  
    ADMIN_PASSWORD = "postgres"
    ```

---

## macOS/Linux Users

The setup script automatically adapts the database credentials for your system:

- **ADMIN_USER**: Your logged-in username (e.g., `whoami`).
- **ADMIN_PASSWORD**: Defaults to `None`.

No manual changes are required unless your PostgreSQL setup uses custom credentials.

---

## Getting Your OpenAI API Key

1. Log in to your [OpenAI account](https://platform.openai.com/).
2. Navigate to **API Keys** in your account settings.
3. Generate a new API key and copy it.
4. Paste the key when prompted during the setup process.

---

## Accessing the Application

1. Open the API documentation in your browser: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
2. Use the **Swagger UI** to interact with the endpoints.

---

## Security Note

- After the Vault root token is used for the first time, it is saved in `vault/root_token.txt`. For security, delete this file:

  ```bash
  rm vault/root_token.txt
  ```
- As a part of macOS/linux, the handling of root_token is handled by default deletion mechanism.

---

## Troubleshooting

### Python Installation Issues

Verify Python is installed and available in your system's PATH:

- **macOS/Linux**: Run the following command:
    ```bash
        python3 --version
    ```

- Windows: Run the following command:
    ```bash
        python --version
    ```
---

### Vault Installation Issues
- macOS/Linux: The setup script installs Vault automatically.
- Windows: Manually install Vault as described in the Installing Vault section above.

---

### Port Conflicts
- Ensure no other processes are using the following ports:
- Port 8200: Used by Vault.
- Port 8000: Used by FastAPI.
T
he setup script attempts to stop these processes automatically.
