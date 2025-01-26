#!/bin/bash

# Navigate to the vault directory
cd "$(dirname "$0")"

# Run Vault server locally
vault server -config=vault_config.hcl
