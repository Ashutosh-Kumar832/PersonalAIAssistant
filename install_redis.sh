#!/bin/bash

REDIS_PORT=6379
REDIS_CONFIG_PATH="./redis_config"

# Function to check if Redis is installed
check_redis() {
  if command -v redis-server >/dev/null 2>&1; then
    echo "Redis is already installed."
    return 0
  else
    echo "Redis is not installed."
    return 1
  fi
}

# Function to install Redis based on OS
install_redis() {
  echo "Installing Redis..."

  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew >/dev/null 2>&1; then
      brew install redis
    else
      echo "Homebrew not installed. Please install Homebrew first."
      exit 1
    fi
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if [[ -f /etc/os-release ]]; then
      . /etc/os-release
      if [[ "$ID" == "ubuntu" || "$ID_LIKE" == "debian" ]]; then
        sudo apt update
        sudo apt install -y redis
      elif [[ "$ID" == "centos" || "$ID_LIKE" == "rhel fedora" ]]; then
        sudo yum install -y redis
      elif [[ "$ID" == "fedora" ]]; then
        sudo dnf install -y redis
      else
        echo "Unsupported Linux distribution: $ID. Please install Redis manually."
        exit 1
      fi
    else
      echo "Cannot detect Linux distribution. Please install Redis manually."
      exit 1
    fi
  elif [[ "$OSTYPE" == "msys"* || "$OSTYPE" == "win32" ]]; then
    # Windows
    echo "Please download and install Redis manually from: https://github.com/MicrosoftArchive/redis/releases"
    exit 1
  else
    echo "Unsupported operating system: $OSTYPE"
    exit 1
  fi

  echo "Redis installed successfully."
}

# Function to start Redis
start_redis() {
  echo "Starting Redis server on port $REDIS_PORT..."

  # Create Redis configuration directory
  mkdir -p "$REDIS_CONFIG_PATH"

  # Start Redis server
  redis-server --port "$REDIS_PORT" > "$REDIS_CONFIG_PATH/redis.log" 2>&1 &

  # Wait for Redis to start
  sleep 2

  # Check if Redis started successfully
  if redis-cli -p "$REDIS_PORT" ping | grep -q "PONG"; then
    echo "Redis server started successfully on port $REDIS_PORT."
  else
    echo "Failed to start Redis server. Check the log file at $REDIS_CONFIG_PATH/redis.log."
    exit 1
  fi
}

# Export Redis configuration to environment variables
export_redis_env() {
  echo "Exporting Redis configuration to environment variables..."
  export REDIS_URL="redis://127.0.0.1:$REDIS_PORT"
  echo "Redis URL: $REDIS_URL"
}

# Main script
if ! check_redis; then
  install_redis
fi

start_redis
export_redis_env

echo "Redis setup complete!"
