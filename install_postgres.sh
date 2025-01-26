#!/bin/bash

# Function to check if PostgreSQL is already installed
check_postgres() {
  if command -v psql >/dev/null 2>&1; then
    echo "PostgreSQL is already installed."
    echo "PostgreSQL version: $(psql --version)"
    return 0
  else
    echo "PostgreSQL is not installed."
    return 1
  fi
}

# Function to install PostgreSQL based on OS
install_postgres() {
  echo "Installing PostgreSQL..."

  # Detect the OS
  if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    if [[ "$ID" == "ubuntu" || "$ID_LIKE" == "debian" ]]; then
      echo "Detected Ubuntu/Debian-based system."
      sudo apt update
      sudo apt install -y postgresql postgresql-contrib
    elif [[ "$ID" == "centos" || "$ID_LIKE" == "rhel fedora" ]]; then
      echo "Detected CentOS/RHEL-based system."
      sudo yum install -y postgresql-server postgresql-contrib
      sudo postgresql-setup initdb
      sudo systemctl start postgresql
      sudo systemctl enable postgresql
    elif [[ "$ID" == "fedora" ]]; then
      echo "Detected Fedora-based system."
      sudo dnf install -y postgresql-server postgresql-contrib
      sudo postgresql-setup --initdb
      sudo systemctl start postgresql
      sudo systemctl enable postgresql
    else
      echo "Unsupported Linux distribution: $ID. Please install PostgreSQL manually."
      exit 1
    fi
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS."
    if command -v brew >/dev/null 2>&1; then
      echo "Using Homebrew to install PostgreSQL."
      brew install postgresql
      brew services start postgresql
    else
      echo "Homebrew not installed. Please install Homebrew and try again."
      exit 1
    fi
  else
    echo "Cannot detect operating system. Please install PostgreSQL manually."
    exit 1
  fi

  echo "PostgreSQL installed successfully."
}

# Main script logic