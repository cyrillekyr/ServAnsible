importimport terraform as tf
from time import sleep
from ssh_keys import SSH
from configparser import ConfigParser
import ipaddress, getpass, os, requests
import subprocess

config_file = "Terraform_Deployment/automation/deployment-configuration.ini"
bloc_title = "lxc-params"

parser = ConfigParser()
parser.read(config_file)
lxc_config = {}
if parser.has_section(bloc_title):
    params = parser.items(bloc_title)
    for param in params:
        lxc_config[param[0]] = param[1]

        try:
            # defining some variables in use
            FIRST_THREE_IPv4_DIGITS = {
                "Wano": {
                    "LAN": "192.168.1",
                    "DMZ": "10.10.10"
                },
                "Narnia": {
                    "LAN": "192.168.10",
                    "DMZ": "10.20.10"
                }
            }

            NET_SEC_BRIDGE = {
                "LAN": "vmbr2",
                "DMZ": "vmbr3"
            }

            IP = lxc_config['proxmox_ip']
            USER = lxc_config['proxmox_user']
            NODE = lxc_config['proxmox_node']
            PASS = subprocess.run(
                f"vault kv get -field=password secret/nodes/{NODE}", 
                check=True, 
                text=True, 
                capture_output=True
            ).stdout

            HOST = lxc_config['ct_hostname']
            NET_SEG = lxc_config['ct_network_segment']

            VMBR = NET_SEC_BRIDGE[NET_SEG]
            DISK_SIZE = lxc_config['ct_disk_size']
            CORES = lxc_config['ct_cores_number']
            MEM = lxc_config['ct_memory_size']
            SWAP = lxc_config['ct_swap_size']
            DESC = lxc_config['ct_description']

            working_dir = "Terraform_Deployment/lxc-vm"
            ssh_public_key = SSH(
                bit_size = 2048,
                _dir = working_dir
            ).load_keys()

            BASE_URL = f"https://{IP}:8006/api2/json"
            response = requests.post(
                f"{BASE_URL}/access/ticket", 
                data={"username": USER,"password": PASS}, 
                verify=False
            ).json()["data"]
            ticket = response["ticket"]

            use_ids = []
            for vm in ["lxc", "qemu"]:
                response = requests.get(
                    f"{BASE_URL}/nodes/{NODE}/{vm}", 
                    cookies={"PVEAuthCookie": ticket}, 
                    verify=False
                ).json()["data"]
                # 
                for i in range(len(response)):
                    use_ids.append(response[i]["vmid"])

                new_vm_id = 100
                while True:
                    if new_vm_id not in use_ids:
                        break
                    new_vm_id += 1

            GWAY = f"{FIRST_THREE_IPv4_DIGITS[NODE][NET_SEG]}.1"
            MASK = lxc_config['ct_net_mask']
            BIN_MASK = "".join(bin(int(number))[2:].zfill(8) for number in MASK.split('.'))
            CIDR = BIN_MASK.count("1")
            IPv4 = f"{FIRST_THREE_IPv4_DIGITS[NODE][NET_SEG]}.{new_vm_id}"
            IPv4_full = f"{IPv4}/{CIDR}"

            # Define the Terraform configuration
            terraform_config = """provider "proxmox" {
    pm_tls_insecure = true
    pm_api_url      = var.pm_api_url
    pm_user         = var.pm_user
    pm_password     = var.pm_password
}

resource "proxmox_lxc" "test_lxc_container" {
    count         = 1
    hostname      = var.vm_hostname
    target_node   = var.pm_target_node
    ostemplate    = "local:vztmpl/${var.vm_ct_template}"
    ostype        = "debian"

    rootfs {
        storage = "local-lvm"
        size    = var.vm_disk_size
    }
    
    network {
        name     = "eth0"
        bridge   = var.vm_bridge_interface
        ip       = var.vm_full_ipv4_address
        ip6      = "auto"
        gw       = var.vm_gw_ipv4_address
        firewall = true
    }

    nameserver   = var.vm_name_server
    searchdomain = var.vm_search_domain

    cores  = var.vm_cores
    memory = var.vm_memory
    swap   = var.vm_swap
    
    features {
        nesting = true 
        fuse    = true
    }

    onboot = true
    # start  = true

    description     = var.vm_description
    ssh_public_keys = <<-EOT
        ${var.ssh_public_key}
    EOT
}

# resource "null_resource" "execute_commands" {
#     provisioner "file" {
#         source      = "Resources/ssham-key"
#         destination = "/root/ssham-key"
#     }

#     provisioner "file" {
#         source      = "Terraform_Deployment/config/users"
#         destination = "/root/users"
#     }

#     provisioner "file" {
#         source      = "Terraform_Deployment/config/users_groups"
#         destination = "/root/users_groups"
#     }

#     provisioner "file" {
#         source      = "Resources/.bashrc"
#         destination = "/root/.bashrc"
#     }

#     provisioner "file" {
#         source      = "Terraform_Deployment/setup/zabbix_agent2.conf"
#         destination = "/root/zabbix_agent2.conf"
#     }

#     provisioner "file" {
#         source      = "Terraform_Deployment/setup/systemd-timesyncd.service"
#         destination = "/root/systemd-timesyncd.service"
#     }

#     provisioner "file" {
#         source      = "Terraform_Deployment/setup/timesyncd.conf"
#         destination = "/root/timesyncd.conf"
#     }

#     provisioner "remote-exec" {
#         script   = "Terraform_Deployment/setup/main.sh"
#     }

#     connection {
#         type        = "ssh"
#         user        = "root"
#         host        = var.vm_ipv4_address
#         private_key = file(var.ssh_private_key_file)
#     }

#     depends_on = [proxmox_lxc.test_lxc_container[0]]
# }
"""

            # Define some variables that will be used by terraform for the deployment Terraform
            terraform_vars = """pm_api_url            = "%s"
pm_user               = "%s"
pm_password           = "%s"
pm_target_node        = "%s"
vm_hostname           = "%s"
vm_disk_size          = "%s"
vm_bridge_interface   = "%s"
vm_full_ipv4_address  = "%s"
vm_ipv4_address       = "%s"
vm_gw_ipv4_address    = "%s"
vm_cores              = %s
vm_memory             = %s
vm_swap               = %s
vm_description        = "%s"
vm_ct_template        = "debian-12-standard_12.7-1_amd64.tar.zst"
ssh_public_key        = "%s"
ssh_private_key_file  = "id_rsa"
""" %(
        BASE_URL, 
        USER, 
        PASS, 
        NODE, 
        HOST,
        DISK_SIZE,
        VMBR,
        IPv4_full,
        IPv4, 
        GWAY,
        CORES,
        MEM,
        SWAP,
        DESC,
        ssh_public_key
    )

            # Go to terraform directory
            os.chdir(working_dir)

            # Save those variables to a file
            with open(f"terraform.tfvars", "w") as stream:
                stream.write(terraform_vars)

            DEPLOYMENT_STEPS = [
                terraform_config,
                terraform_config.replace("# start", "start"),
                terraform_config.replace("# ", "")
            ]

            # Create the infrastructure
            for step in range(len(DEPLOYMENT_STEPS)):
                builder = DEPLOYMENT_STEPS[step]
                # Save terraform_config_step to a file
                with open(f"main.tf", "w") as stream:
                    stream.write(builder)
                # Building a step
                print(tf.terraform_init())
                print(tf.terraform_apply(skip_plan=True))
                print(tf.terraform_output())
                # wait until the CT boots
                if step == 1:
                    sleep(30)

            print(f"\nA file named \"{working_dir}/id_rsa\" has been generated in the current folder. Use it so as to log in to the new deployed VM.")
        except Exception as e:
            print(f"Error : {str(e)}.")

else:
    raise Exception(f"Section {bloc_title} has not been found in {config_file} file.")