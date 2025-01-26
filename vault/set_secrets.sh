#!/bin/bash

# Set Vault address and token
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Check if Vault server is running
if ! curl -s $VAULT_ADDR/v1/sys/health | grep -q '"initialized":true'; then
  echo "Vault server is not running. Start the server first."
  exit 1
fi

# Add the OpenAI API key to the Vault
read -p "Enter your OpenAI API key: " OPENAI_API_KEY
vault kv put secrets/openai openai_key="$OPENAI_API_KEY"

echo "OpenAI API key stored in Vault."
