#!/bin/bash
# Servansible Requirements Installer

# Install Ansible
if ! command -v ansible &> /dev/null
then
    echo "Installing Ansible..."
    sudo apt update && sudo apt install -y ansible
fi

# Install Python (if not already installed)
if ! command -v python3 &> /dev/null
then
    echo "Installing Python3..."
    sudo apt install -y python3 python3-pip
fi

# Install SSHpass (for password-based SSH connections, optional)
if ! command -v sshpass &> /dev/null
then
    echo "Installing SSHpass..."
    sudo apt install -y sshpass
fi

# Install Docker (if needed for Docker container management)
if ! command -v docker &> /dev/null
then
    echo "Installing Docker..."
    sudo apt install -y docker.io
fi

# Install JQ for JSON parsing (if needed)
if ! command -v jq &> /dev/null
then
    echo "Installing jq..."
    sudo apt install -y jq
fi


# Install HashiCorp Vault
if ! command -v vault &> /dev/null
then
    echo "Installing HashiCorp Vault..."
    curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
    sudo apt update && sudo apt install -y vault
fi

echo "All dependencies are installed!"
