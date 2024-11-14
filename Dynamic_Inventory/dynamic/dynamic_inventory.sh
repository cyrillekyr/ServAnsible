#! /bin/bash

source config.sh

PROXMOX_PASSWORD=$(vault kv get -field=password secret/nodes/pve)

python3 Dynamic_Inventory/dynamic/proxmox.py --url=https://192.168.10.106:8006/ --username=root@pam --password=$PROXMOX_PASSWORD --trust-invalid-certs --list --pretty > Dynamic_Inventory/dynamic/pve.json

python3 Dynamic_Inventory/dynamic/process.py Dynamic_Inventory/dynamic/config.json

