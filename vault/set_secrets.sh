#!/bin/bash

export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# Check if Vault is running
if ! curl -s $VAULT_ADDR/v1/sys/health | grep -q '"initialized":true'; then
  echo "Vault server is not running. Start the server first."
  exit 1
fi

# Create Vault policy
cat <<EOF > openai-policy.hcl
path "secret/data/openai" {
  capabilities = ["read"]
}
EOF

vault policy write openai-policy openai-policy.hcl
rm openai-policy.hcl

# Add the OpenAI API key
read -p "Enter your OpenAI API key: " OPENAI_API_KEY
vault kv put secret/openai api_key="$OPENAI_API_KEY"
echo "OpenAI API key stored in Vault."
