#!/bin/bash

source "./Log_Management/logger.sh"
source config.sh

# JSON file containing the node information
NODES_FILE="Dynamic_Inventory/dynamic/config.json"

# Function to store the password in Vault
store_password_in_vault() {
    local node_name=$1
    local password=$2

    # Command to store the password in Vault
    vault kv put secret/nodes/$node_name password=$password
}

echo "[+] Vault Configuration"

# Check if Vault is correctly configured
if ! vault status > /dev/null 2>&1; then
    echo "Vault is not accessible or properly configured. Please check your Vault setup."
    general_log "${LOG_LEVEL[1]}" "${SERVICE[3]}" "Vault is not accessible or properly configured. Please check your Vault setup."
    exit 1
fi

# Read the node information from the JSON file
nodes=$(jq -r '.nodes[] | .noeud' $NODES_FILE)

# Loop through each node and ask for the password
for node in $nodes; do
    echo "Please enter the password for node $node:"
    read -s password

    # Store the password in Vault
    store_password_in_vault $node $password

    echo "Password for $node successfully stored in Vault."
    general_log "${LOG_LEVEL[1]}" "${SERVICE[3]}" "Password for $node successfully stored in Vault."
done

echo "All passwords have been stored."