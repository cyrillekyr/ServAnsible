#! /bin/bash

source config.sh

PROXMOX_PASSWORD=$(vault kv get -field=password secret/nodes/node1)

python3 $INVENTORIES/dynamic/proxmox.py --url=hub.com --username=user --password=$PROXMOX_PASSWORD --trust-invalid-certs --list --pretty > ../inventories/dynamic/node1.json

python3 $INVENTORIES/dynamic/process.py config.json

