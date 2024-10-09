#! /bin/bash

source config.sh

#PROXMOX_PASSWORD=$(vault kv get -field=password secret/nodes/node1)

python3 Dynamic_Inventory/dynamic/proxmox.py --url=https://192.168.10.106:8006/ --username=root@pam --password=Uranus82 --trust-invalid-certs --list --pretty > Dynamic_Inventory/dynamic/node1.json

python3 Dynamic_Inventory/dynamic/process.py Dynamic_Inventory/dynamic/config.json

