import terraform as tf
from time import sleep
from ping3 import ping
from ssh_keys import SSH
from configparser import ConfigParser
import ipaddress, getpass, os, requests

config_file = "Terraform_Deployment/automation/deployment-configuration.ini"
bloc_title = "qemu-vm-params"

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

        HOST = lxc_config['vm_hostname']
        NET_SEG = lxc_config['vm_network_segment']   

        VMBR = NET_SEC_BRIDGE[NET_SEG]
        DISK_SIZE = lxc_config['vm_disk_size']
        CORES = lxc_config['vm_cores_number']
        MEM = lxc_config['vm_memory_size']
        DESC = lxc_config['vm_description']

        working_dir = "Terraform_Deployment/qemu-vm"
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
        MASK = lxc_config['vm_net_mask']
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

resource "null_resource" "resize_disk" {
    provisioner "remote-exec" {
        inline = ["qm disk resize ${var.vm_ci_template_id} scsi0 ${var.vm_disk_size}"]
    }

    connection {
        type        = "ssh"
        user        = var.pm_host_user
        host        = var.pm_host_ip
        password    = var.pm_password
    }
}

resource "proxmox_vm_qemu" "test_vm" {
    count       = 1
    name        = var.vm_hostname
    desc        = var.vm_description
    target_node = var.pm_target_node

    clone      = var.vm_ci_template
    full_clone = true

    network {
      model     = "virtio"
      bridge    = var.vm_bridge_interface
      firewall  = true
      link_down = false
    }

    ciuser       = var.vm_ci_user
    cipassword   = var.vm_ci_password
    sshkeys      = var.vm_ci_pubkey
    ipconfig0    = var.vm_ci_netconf
    searchdomain = var.vm_ci_domain
    nameserver   = var.vm_ci_dnserv

    scsihw  = "virtio-scsi-pci"
    hotplug = "disk,network,usb"
    cpu     = "x86-64-v2-AES"
    kvm     = false
    onboot  = true
    
    cores    = var.vm_cores
    bootdisk = "scsi0"
    memory   = var.vm_memory
    sockets  = 1

    depends_on = [null_resource.resize_disk[0]]
}

# resource "null_resource" "execute_commands" {
#     provisioner "file" {
#         source      = "Terraform_Deployment/config/ssham-key"
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
#         source      = "Terraform_Deployment/setup/.bashrc"
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

#     depends_on = [proxmox_vm_qemu.test_vm[0]]
# }
"""

        # Define some variables that will be used by terraform for the deployment Terraform
        terraform_vars = """pm_api_url            = "%s"
pm_user               = "%s"
pm_password           = "%s"
pm_target_node        = "%s"
pm_host_user          = "%s"
pm_host_ip            = "%s"
vm_hostname           = "%s"
vm_description        = "%s"
vm_ci_template        = "%s"
vm_ci_template_id     =  %s
vm_disk_size          = "%s"
vm_ci_user            = "%s"
vm_ci_password        = "%s"
vm_ci_pubkey          = "%s"
vm_ci_netconf         = "%s"
vm_bridge_interface   = "%s"
vm_ci_domain          = "tettrix.infra"
vm_ci_dnserv          = "%s"
vm_cores              =  %s
vm_memory             =  %s
vm_ipv4_address       = "%s"
ssh_private_key_file  = "id_rsa"
""" %(
    BASE_URL, 
    USER, 
    PASS, 
    NODE,
    USER.split("@")[0],
    IP,
    HOST,
    DESC,
    lxc_config['vm_ci_template'],
    lxc_config['vm_ci_template_id'],
    DISK_SIZE,
    lxc_config['vm_ci_user'],
    lxc_config['vm_ci_password'],
    ssh_public_key,
    f"ip={IPv4_full},gw={GWAY}",
    VMBR,
    GWAY,
    CORES,
    MEM,
    IPv4
)

        # Go to terraform directory
        os.chdir(working_dir)

        # Save those variables to a file
        with open(f"terraform.tfvars", "w") as stream:
            stream.write(terraform_vars)

        DEPLOYMENT_STEPS = [
            terraform_config,
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
            # wait until the VM get alive on the network
            while not ping(IPv4):
                sleep(3)

        print(f"\nA file named \"{working_dir}/id_rsa\" has been generated in the current folder. Use it so as to log in to the new deployed VM.")
    except Exception as e:
        print(f"Error : {str(e)}.")

else:
    raise Exception(f"Section {bloc_title} has not been found in {config_file} file.")