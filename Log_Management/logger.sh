#!/bin/bash

parse_ansible_output() {
    local ansible_output="$1"
    local log_message=""

    # Extracting all hosts from the play recap
    hosts=$(grep -oP '^[\d\.\-]+.*(?= : ok=)' "$ansible_output")

    # Loop through each host and capture its statuses
    while IFS= read -r host; do
        ok_count=$(grep "$host" "$ansible_output" | awk -F "ok=" '{print $2}' | awk '{print $1}')
        changed_count=$(grep "$host" "$ansible_output" | awk -F "changed=" '{print $2}' | awk '{print $1}')
        unreachable_count=$(grep "$host" "$ansible_output" | awk -F "unreachable=" '{print $2}' | awk '{print $1}')
        failed_count=$(grep "$host" "$ansible_output" | awk -F "failed=" '{print $2}' | awk '{print $1}')
        skipped_count=$(grep "$host" "$ansible_output" | awk -F "skipped=" '{print $2}' | awk '{print $1}')
        rescued_count=$(grep "$host" "$ansible_output" | awk -F "rescued=" '{print $2}' | awk '{print $1}')
        ignored_count=$(grep "$host" "$ansible_output" | awk -F "ignored=" '{print $2}' | awk '{print $1}')

        # Determine the overall status
        if [[ $unreachable_count -gt 0 ]]; then
            status="UNREACHABLE"
        elif [[ $failed_count -gt 0 ]]; then
            status="FAILED"
        elif [[ $changed_count -gt 0 ]]; then
            status="CHANGED"
        else
            status="OK"
        fi

        # Construct the log message for each host
        log_message+="Host: $host\n"
        log_message+="  Status: $status\n"
        log_message+="  ok: $ok_count, changed: $changed_count, unreachable: $unreachable_count, failed: $failed_count, skipped: $skipped_count, rescued: $rescued_count, ignored: $ignored_count\n\n"
    done <<< "$hosts"

    # Return the constructed log message
    echo -e "$log_message"
}

generate_log() {
    local level=$1
    local service=$2
    local user_message=$3
    local timestamp=$(date -u +"%s")
    local user=$(whoami)
    local ip=$(hostname -I | awk '{print $1}')

    # Call parse_ansible_output and capture the output
    local ansible_status=$(parse_ansible_output "ansible_output.log")

    # Combine user message and ansible status
    local final_message
    final_message=$(printf "%s\n\n%s" "$user_message" "$ansible_status")


    # Create a JSON log
    log=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "level": "$level",
  "service": "$service",
  "user": "$user",
  "ip": "$ip",
  "message": "$final_message"
}
EOF
)

    # Save to the log file
    echo "$log" >> servansible.log
    echo "Log saved to servansible.log"
}

general_log() {
    local level=$1
    local service=$2
    local message=$3
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local user=$(whoami)
    local ip=$(hostname -I | awk '{print $1}')

    # Créer un log JSON
    log=$(cat <<EOF
{
  "timestamp": "$timestamp",
  "level": "$level",
  "service": "$service",
  "user": "$user",
  "ip": "$ip",
  "message": "$message"
}
EOF
)

    # Sauvegarder dans le fichier log
    echo "$log" >> servansible.log
    echo "Log saved to servansible.log"
}