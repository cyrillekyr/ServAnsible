# Servansible

**Servansible** is a modular toolbox built on Ansible, designed to manage server configurations, user and group management, server availability checks, dynamic inventory generation, log management, and HashiCorp Vault integration for storing sensitive credentials. This project provides a streamlined solution for automating server administration tasks.

## Prerequisites

Ensure you have the following installed:

- Bash (required for executing scripts)
- Ansible (for running the playbooks)
- HashiCorp Vault (for managing node credentials)
- Python (for Ansible and Vault modules)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/servansible.git
    cd servansible
    ```

2. Install dependencies by executing the `requirements.sh` script:
    ```bash
    bash requirements.sh
    ```

3. Customize the configuration file (`config.sh`) with your node and group details:
    ```bash
    nano config.sh
    ```

4. Define server nodes and groups in `Dynamic_Inventory/dynamic/dynamic_inventory.sh`:
    ```bash
    nano Dynamic_Inventory/dynamic/dynamic_inventory.sh
    ```

## Setting Up Vault for Storing Node Passwords

To set up HashiCorp Vault for storing passwords for each node, run the following command:

```bash
bash servansible.sh setup-vault
```

This will configure Vault to securely manage passwords for all defined nodes.

# Inventory Setup

To generate a dynamic inventory of the available servers, use the following command:
```bash
bash servansible.sh dynamic
```

This will create a list of servers based on the configuration provided in `Dynamic_Inventory`



