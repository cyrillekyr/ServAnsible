import os
from automation.ssh_keys import SSH
from automation.utils import getBooInput, getBridgeInt, getInteger, getInput, getIP, getNetID, getPassword


def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    display = """ CAPTION : Terraform VMs builder on Proxmox VE

    What kind of VM do you wanna deploy ?
      Enter '1' for LXC container
      Enter '2' for Qemu-VM
"""
    print(display)

    user_choice = None

    while True:
        try:
            user_choice = int(input(" Your choice : "))
        except KeyboardInterrupt:
            exit()
        except:
            continue

        if user_choice in [1, 2]:
                break

    return user_choice


def proxmox():
    os.system('cls' if os.name == 'nt' else 'clear')

    print(" CAPTION : Terraform VMs builder on Proxmox VE\n\n    To help us connect to the Proxmox VE API, we need the following information from you:")

    proxmox_ip = getIP(" The Proxmox Host IP : ")
    proxmox_node = getInput(" The Proxmox node name : ")
    proxmox_user = getInput(" The Proxmox Host user (<username>@<realm>) : ")
    proxmox_user_password = getPassword(" The Proxmox Host user password : ")

    proxmox_yaml = "proxmox:\n  api_url: %s\n  ip: %s\n  node: %s\n  user:\n    name: %s\n    password: %s" %(
        f"https://{proxmox_ip}:8006/api2/json", proxmox_ip, proxmox_node, proxmox_user, 
        proxmox_user_password
    )

    return proxmox_yaml


def lxc(
    proxmox_node : str,
    working_dir : str,
    vm_id : int
):
    os.system('cls' if os.name == 'nt' else 'clear')

    print(" CAPTION : Terraform VMs builder on Proxmox VE\n\n    To configure the LXC container for deployment purposes, please provide the following details:\n")

    lxc_hostname = getInput(" The CT hostname : ")
    lxc_cores = getInteger(" The CT cores number : ")
    lxc_memory = getInteger(" The CT memory size : ")
    lxc_disk = getInput(" The CT disk size : ")
    lxc_swap = getInteger(" The CT swap size : ")
    lxc_domain = "tettrix.infra" # getInput(" The domain name to apply on that CT : ")
    lxc_template = "debian-12-standard_12.7-1_amd64.tar.zst" # getInput(" The template on which the CT will be built on : ")
    lxc_network_segment = getInput(" The network segment on which the CT will be placed (pan/wan/lan/dmz) : ").upper()
    lxc_network_bridge = getBridgeInt(desired_network_segment=lxc_network_segment)
    static_ip_setup = getBooInput(" Do you want to configure IPv4 addressing on the CT ? (y/n) : ")
    lxc_desc = getInput(" A brief description about the CT : ")

    print("\n    By default, a root account will be setup on the CT. Please, provide a password to bind to that account:\n")
    lxc_root_password = getPassword(" The password to set for the user 'root' on the CT : ")
    lxc_root_ssh_public_key = SSH(
        bit_size = 2048,
        _dir = working_dir
    ).load_keys()

    # print("\n    Here comes information related to network settings. Please, provide us the correct answer:\n")
    # lxc_network_segment = getInput(" The network segment on which the CT will be placed (pan/wan/lan/dmz) : ").upper()
    # lxc_network_bridge = getBridgeInt(desired_network_segment=lxc_network_segment)

    lxc_yaml = "lxc:\n  hostname: %s\n  cores: %d\n  memory: %d\n  disk: %s\n  swap: %d\n  template: %s\n  domain: %s\n  description: %s\n  user:\n    name: root\n    password: %s\n    ssh_public_key: %s\n  network:\n    segment: %s\n    bridge: %s" %(
        lxc_hostname, lxc_cores, lxc_memory, lxc_disk, lxc_swap, lxc_template, lxc_domain, lxc_desc,
        lxc_root_password, lxc_root_ssh_public_key, lxc_network_segment, lxc_network_bridge
    )

    if static_ip_setup:
        net_id = getNetID(
            proxmox_api_node=proxmox_node, 
            desired_network_segment=lxc_network_segment
        ) or "192.168.10"
        lxc_yaml += "\n    ip: %s\n    gw: %s" %(
            f"{net_id}.{vm_id}/24",
            f"{net_id}.1"
        )

    return lxc_yaml


def qemu(
    proxmox_node : str,
    working_dir : str,
    vm_id : int
):
    os.system('cls' if os.name == 'nt' else 'clear')

    print(" CAPTION : Terraform VMs builder on Proxmox VE\n\n    To configure the Qemu VM for deployment purposes, please provide the following details:\n")

    qemu_hostname = getInput(" The VM hostname : ")
    qemu_cores = getInteger(" The VM cores number : ")
    qemu_memory = getInteger(" The VM memory size : ")
    qemu_disk = getInput(" The VM disk size : ")
    # qemu_cloudinit_template_id = 9000 # getInput(" The template VM ID on which the VM will be built on : ")
    qemu_cloudinit_template = "debian-12-cloudinit-template" # getInput(" The template name on which the VM will be built on : ")
    qemu_domain = "tettrix.infra" # getInput(" The domain name to apply on that VM : ")
    qemu_desc = getInput(" A brief description about the VM : ")

    print("\n    By default, a root account will be setup on the VM. Please, provide a password to bind to that account:\n")
    qemu_root_password = getPassword(" The password to set for the user 'root' on the VM : ")
    qemu_root_ssh_public_key = SSH(
        bit_size = 2048,
        _dir = working_dir
    ).load_keys()

    print("\n    Here comes information related to network settings. Please, provide us the correct answer:\n")
    qemu_network_segment = getInput(" The network segment on which the VM will be placed : ").upper()
    qemu_network_bridge = getBridgeInt(desired_network_segment=qemu_network_segment)

    qemu_yaml = "qemu:\n  hostname: %s\n  cores: %d\n  memory: %d\n  disk: %s\n  description: %s\n  cloudinit:\n    template: %s\n    domain: %s\n    : %s\n    user:\n      name: root\n      password: %s\n      ssh_public_key: %s\n    network:\n      segment: %s\n      bridge: %s" %(
        qemu_hostname, qemu_cores, qemu_memory, qemu_disk, qemu_desc, qemu_cloudinit_template, qemu_root_password,
        qemu_root_ssh_public_key, qemu_network_segment, qemu_network_bridge
    )

    static_ip_setup = getBooInput("\n Do you want to configure IPv4 addressing on the VM ? (y/n) : ")
    if static_ip_setup:
        net_id = getNetID(
            proxmox_api_node=proxmox_node, 
            desired_network_segment=qemu_network_segment
        )
        qemu_yaml += "\n    ip: %s\n    gw: %s" %(
            f"{net_id}.{vm_id}/24",
            f"{net_id}.1"
        )

    return qemu_yaml


# print(lxc("Wano", ".", 100))

# subprocess.run(
#     f"vault kv get -field=password secret/nodes/{NODE}", 
#     check=True, 
#     text=True, 
#     capture_output=True
# ).stdout