#!/bin/bash


source "./Log_Management/logger.sh"
source config.sh


# Function to display help
function show_help() {
    echo "Usage: $0 action [options]"
    echo "Actions:"
    echo "  adduser    Add a user"
    echo "  deluser    Delete a user"
    echo "  addgroup   Add a group"
    echo "  delgroup   Delete a group"
    echo "  setup-serv Deploy default configurations on a server"
    echo "  dynamic    Dynamic Inventory"
    echo "  ls-groups   List all available server groups"
    echo "  list-servers  List all available servers"
    echo "  list-nodes    List all nodes"
    echo "  pingtest      Check servers Availability"
    echo "  setup-vault   Setup passwords for nodes"
    echo ""
    echo "Options:"
    echo "  -a              Deploy on all servers"
    echo "  -n          Specify a node"
    echo "  -s SERVERLIST   Specify servers (comma-separated)"
    echo "  -g GROUP        Specify a group of servers"
    echo "  -h              Display help"
    exit 0
}

# Function to list available server groups
function list_groups() {
    json_file="Dynamic_Inventory/dynamic/config.json"
    
    # Check if the file exists
    if [[ ! -f "$json_file" ]]; then
        echo "Error: File $json_file not found!"
        return 1
    fi
    
    # Extract groups using jq and convert them to lowercase
    groups=$(jq -r '.groups[]' "$json_file" | tr '[:upper:]' '[:lower:]')

    # Display the groups in the required format
    echo "Available groups:"
    for group in $groups; do
        echo "- $group"
    done
    exit 0
}

list_nodes() {
    # Charger directement config.json
    local config_file="Dynamic_Inventory/dynamic/config.json"

    # Vérifier si le fichier existe
    if [[ ! -f "$config_file" ]]; then
        echo "Fichier $config_file introuvable."
        return 1
    fi

    # Utiliser jq pour extraire et lister les noms des nœuds
    nodes=$(jq -r '.nodes[] | .noeud' "$config_file")
    for node in $nodes; do
        echo "- $node"
    done
    exit 0

}


# Function to list available servers
function list_servers() {
    #dynamic_inventory
    echo "[+] Available servers"
    inventory_file="Dynamic_Inventory/all.hosts"
    
    # Check if the file exists
    if [[ ! -f "$inventory_file" ]]; then
        echo "Error: File $inventory_file not found!"
        return 1
    fi

    echo "Listing all servers from the inventory:"
    awk '
    # Match group names (lines starting with [ and ending with ])
    /^\[.*\]$/ {
        group = $0; 
        print group;
        next
    }
    # Match server entries (lines that contain ansible_host)
    /^[^#]+ ansible_host=/ {
        split($0, arr, " ");
        server = arr[1]
        print "  - " server
    }
    ' "$inventory_file"

    #Logic for listing servers
}

# Function to test servers availability 
function pingtest() {
    #dynamic_inventory
    # Define the command to run the Ansible ping
    ANSIBLE_CMD="ansible all -i Dynamic_Inventory/all.hosts -m ping"
    # Run the Ansible command and capture the output
    OUTPUT=$(eval "$ANSIBLE_CMD")

    # Initialize arrays to store the results
    SUCCESS_SERVERS=()
    UNREACHABLE_SERVERS=()

    # Process the output to categorize and clean up the results
    while IFS= read -r line; do
        if [[ "$line" == *"SUCCESS"* ]]; then
            SERVER_NAME=$(echo "$line" | cut -d' ' -f1)
            SUCCESS_SERVERS+=("$SERVER_NAME")
        elif [[ "$line" == *"UNREACHABLE"* ]]; then
            SERVER_NAME=$(echo "$line" | cut -d' ' -f1)
            UNREACHABLE_SERVERS+=("$SERVER_NAME")
        fi
    done <<< "$OUTPUT"

    # Display the results grouped by status
    echo "Server Availability Report:"
    echo "==========================="

    echo -e "\033[32mAvailable Servers:\033[0m"
    for server in "${SUCCESS_SERVERS[@]}"; do
        echo -e "\033[32m$server\033[0m"
    done

    echo -e "\033[31m\nUnreachable Servers:\033[0m"
    for server in "${UNREACHABLE_SERVERS[@]}"; do
        echo -e "\033[31m$server\033[0m"
    done

    # Summary
    echo -e "\nSummary:"
    echo "========"
    echo -e "Available Servers: \033[32m${#SUCCESS_SERVERS[@]}\033[0m"
    echo -e "Unreachable Servers: \033[31m${#UNREACHABLE_SERVERS[@]}\033[0m"

    
}

function setup-vault() {
    bash Vault_configuration/setup-vault.sh
}

function dynamic_inventory() {
    echo "Starting Dynamic Inventory ....."
    bash Dynamic_Inventory/dynamic/dynamic_inventory.sh
    general_log "${LOG_LEVEL[0]}" "${SERVICE[2]}" "Dynamic Inventory"
}

# Target determination and action application
function perform_action() {
    local action=$1
    local message=$2
    local target=$3  # User or group

    

    # Simulated logic based on the action
    case "$action" in
        adduser)
            echo "Adding users to $message..."
            ansible-playbook -i "$target" User_Management/create_user.yml | tee ansible_output.log
            users=$(grep -E 'name:' User_Management/data/users_groups.yaml | sed 's/.*name: "\(.*\)".*/\1/' | paste -sd "," -)
            generate_log "${LOG_LEVEL[1]}" "${SERVICE[0]}" "Adding users $users on $message"

            ;;
        deluser)
            echo "Deleting users from $message..."
            # Insert Ansible or bash logic for deleting user
            ansible-playbook -i "$target" User_Management/delete_user.yml
            users=$(grep -E '^\s*-\s*"' User_Management/data/users.yaml | sed 's/.*- "\(.*\)".*/\1/' | paste -sd "," -)
            generate_log "${LOG_LEVEL[1]}" "${SERVICE[0]}" "Deleting users "$users" from $message"
            ;;
        addgroup)
            echo "Adding group to $message..."
            # Insert Ansible or bash logic for adding group
            ansible-playbook -i "$target" User_Management/create_group.yml
            groups=$(grep -E '^\s*-\s*"' User_Management/data/groups.yaml | sed 's/.*- "\(.*\)".*/\1/' | paste -sd "," -)
            generate_log "${LOG_LEVEL[1]}" "${SERVICE[0]}" "Adding groups $groups on $message"
            ;;
        delgroup)
            echo "Deleting group from $message..."
            # Insert Ansible or bash logic for deleting group
            ansible-playbook -i "$target" User_Management/delete_group.yml
            groups=$(grep -E '^\s*-\s*"' User_Management/data/groups.yaml | sed 's/.*- "\(.*\)".*/\1/' | paste -sd "," -)
            generate_log "${LOG_LEVEL[1]}" "${SERVICE[0]}" "Deleting groups $groups from $message"
            ;;
        setup-serv)
            echo "Deploying default configurations on $message"
            ansible-playbook -i "$target" Server_Setup/default_users.yaml
            generate_log "${LOG_LEVEL[1]}" "${SERVICE[0]}" "Deploying default configurations on $message"
            ;;
        *)
            echo "Error: Invalid action '$action'."
            show_help
            ;;
    esac
}



# Parse the action
ACTION=$1
shift  # Shift to process options

# Initialize variables
ALL_SERVERS=false
SERVER_LIST=""
GROUP=""


# Actions that don't require options
NO_OPTION_ACTIONS=("dynamic" "ls-groups" "list-servers" "list-nodes" "pingtest" "setup-vault")

# Function to check if the action is in the NO_OPTION_ACTIONS array
function is_no_option_action() {
    local action="$1"
    for no_option_action in "${NO_OPTION_ACTIONS[@]}"; do
        if [[ "$no_option_action" == "$action" ]]; then
            return 0  # True, action found in the array
        fi
    done
    return 1  # False, action not found
}

# Check for action
if is_no_option_action "$ACTION"; then
    # If it's an action that doesn't require options, ensure no extra options are passed
    if [[ "$#" -gt 0 ]]; then
        echo "Error: Action '$ACTION' does not require any options."
        show_help
    fi
    case "$ACTION" in
        pingtest)
            pingtest
            ;;
        ls-groups)
            list_groups
            ;;
        list-nodes)
            list_nodes
            ;;
        list-servers)
            list_servers
            ;;
        dynamic)
            dynamic_inventory
            ;;
        setup-vault)
            setup-vault
            ;;
    esac
    exit 0
fi

# Parse options for actions that require options
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -a) ALL_SERVERS=true ;;
        -s) SERVER_LIST=$2; shift ;;
        -g) GROUP=$2; shift ;;
        -n) NODE=$2; shift ;;
        -h) show_help ;;
        *) echo "Unknown option: $1"; show_help ;;
    esac
    shift
done

# Check for conflicting options

if [[ "$ALL_SERVERS" == true && -n "$GROUP" ]]; then
    echo "Error: You cannot use -a with -g."
    show_help
fi

if [[ "$ALL_SERVERS" == true && -n "$NODE" ]]; then
    echo "Error: You cannot use -a with -n."
    show_help
fi

if [[ "$ALL_SERVERS" == true && -n "$SERVER_LIST" ]]; then
    echo "Error: You cannot use -a with -s."
    show_help
fi

if [[ -n "$NODE" && -n "$SERVER_LIST" ]]; then
    echo "Error: You cannot specify both -n and -s."
    show_help
fi



# Determine the target and perform the corresponding action
if [[ "$ALL_SERVERS" == true ]]; then
    perform_action "$ACTION" "all servers" "Dynamic_Inventory/all.hosts" # Or $GROUP depending on action
elif [[ -n "$NODE" ]]; then
    if [[ -n "$GROUP" ]]; then
        node=$(echo "$NODE" | tr '[:upper:]' '[:lower:]')
        group=$(echo "$GROUP" | tr '[:upper:]' '[:lower:]')
        perform_action "$ACTION" "group '$GROUP' in node '$NODE'" "Dynamic_Inventory/nodes/$node/group_vars/$group.hosts" # Or $GROUP
    else
        perform_action "$ACTION" "all servers in node '$NODE'" "Dynamic_Inventory/nodes/$node/hosts" # Or $GROUP
    fi
elif [[ -n "$SERVER_LIST" ]]; then
    IFS=',' read -r -a servers <<< "$SERVER_LIST"
    for server in "${servers[@]}"; do
        perform_action "$ACTION" "servers '$server'" "$server," # Or $GROUP
    done
else
    echo "Error: You must specify an option for deployment (-a, -s, or -n)."
    show_help
fi



