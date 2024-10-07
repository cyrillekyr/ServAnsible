#!/bin/bash

generate_log() {
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

# Exemple d'utilisation

#generate_log "$level" "$service" "$message"
