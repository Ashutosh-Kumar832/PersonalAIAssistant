#!/bin/bash

# Navigate to the vault directory
cd "$(dirname "$0")"

# Run Vault server on port 8200
vault server -config=vault_config.hcl
