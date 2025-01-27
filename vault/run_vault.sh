#!/bin/bash

# Navigate to the vault directory
cd "$(dirname "$0")"

# Start Vault server and capture the logs
vault server -config=vault_config.hcl > vault_logs.txt 2>&1 &

# Wait for the server to start
sleep 5

# Extract the root token from the logs
ROOT_TOKEN=$(grep -oP '(?<=Root Token: ).*' vault_logs.txt | head -1)

if [ -z "$ROOT_TOKEN" ]; then
  echo "Failed to retrieve the root token."
  exit 1
fi

echo "Root Token: $ROOT_TOKEN"
echo $ROOT_TOKEN > root_token.txt
