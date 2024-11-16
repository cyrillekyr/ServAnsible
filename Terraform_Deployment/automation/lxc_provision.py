from automation import utils
import ipaddress, getpass, os, requests, shutil, subprocess


def run(
    terraform_config : str,
    working_dir : str,
    data : str
):
    try:
        lxc_ip_scheme = data['lxc']['network'].get('ip', None)
        lxc_ip = None
        if lxc_ip_scheme:
            lxc_ip = lxc_ip_scheme.split("/")[0]
        lxc_gateway = data['lxc']['network'].get('gw', None)

        # Go to terraform directory
        os.chdir(working_dir)

        # Define some variables that will be used by terraform for the deployment Terraform
        terraform_vars = """pm_api_url            = "%s"
pm_user               = "%s"
pm_password           = "%s"
pm_target_node        = "%s"
vm_hostname           = "%s"
vm_root_password      = "%s"
vm_disk_size          = "%s"
vm_search_domain      = "%s"
vm_bridge_interface   = "%s"
vm_cores              =  %s
vm_memory             =  %s
vm_description        = "%s"
vm_ct_template        = "%s"
ssh_public_key        = "%s"
vm_swap               =  %s""" %(
    data['proxmox']['api_url'],
    data['proxmox']['user']['name'],
    data['proxmox']['user']['password'],
    data['proxmox']['node'],
    data['lxc']['hostname'],
    data['lxc']['user']['password'],
    data['lxc']['disk'],
    data['lxc']['domain'],
    data['lxc']['network']['bridge'],
    data['lxc']['cores'],
    data['lxc']['memory'],
    data['lxc']['description'],
    data['lxc']['template'],
    data['lxc']['user']['ssh_public_key'],
    data['lxc']['swap']
)

        if not (lxc_ip and lxc_gateway):
            terraform_vars += "\nvm_ip_4_scheme        = \"dhcp\"\n"
        else:
            terraform_vars += "\nvm_ip_4_address        = \"%s\"\nvm_ip_4_scheme        = \"%s\"\nvm_gw_ip_4        = \"%s\"\nvm_name_server        = \"%s\"\n" %(
                lxc_ip, lxc_ip_scheme, lxc_gateway, lxc_gateway
            )
            terraform_config = terraform_config.replace("# #gw", "gw")

        # Save those variables to a file
        with open(f"terraform.tfvars", "w") as stream:
            stream.write(terraform_vars)

        DEPLOYMENT_STEPS = [
            terraform_config,
            terraform_config.replace("# start", "start"),
            terraform_config.replace("# ", "")
        ]

        # Create the infrastructure
        utils.buildVmOnProxmox(
            DEPLOYMENT_STEPS=DEPLOYMENT_STEPS,
            ip_4_set=lxc_ip
        )

        print(f"\nA file named \"{working_dir}/id_rsa\" has been generated in the current folder. Use it so as to log in to the new deployed VM.")
    except Exception as e:
        print(f"Error : {str(e)}.")

















# MASK = lxc_config['ct_net_mask']
# BIN_MASK = "".join(bin(int(number))[2:].zfill(8) for number in MASK.split('.'))
# CIDR = BIN_MASK.count("1")
# IPv4 = f"192.168.10.{new_vm_id}" # f"{FIRST_THREE_IPv4_DIGITS[NODE][NET_SEG]}.{new_vm_id}"
# IPv4_full = f"{IPv4}/{CIDR}"
