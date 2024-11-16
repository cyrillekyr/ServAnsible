from time import sleep
from ping3 import ping
from typing import List
from datetime import datetime
from automation import terraform as tf
import getpass, ipaddress, requests, yaml


def getNetID(
    proxmox_api_node : str,
    desired_network_segment : str
) -> str:
    """ The goal was to return the network id bound to a network segment on a specific proxmox node on the infra """
    try:
        user_node = proxmox_api_node.capitalize()
        user_netseg = desired_network_segment.upper()

        node_netseg_netid = {
            "Wano": {
                "WAN": "172.18.1",
                "LAN": "192.168.1",
                "DMZ": "10.10.10"
            },
            "Narnia": {
                "WAN": "172.19.1",
                "LAN": "192.168.10",
                "DMZ": "10.20.10"
            }
        }

        return node_netseg_netid[user_node][user_netseg]
    except:
        return None


def getBridgeInt(
    desired_network_segment : str
) -> str:
    """ The goal was to give back the bridge interface bound to a particular network segment """
    try:
        user_netseg = desired_network_segment.upper()

        netseg_bridge = {
            "PAN": "vmbr0",
            "WAN": "vmbr1",
            "LAN": "vmbr2",
            "DMZ": "vmbr3"
        }

        return netseg_bridge[user_netseg]
    except:
        return None


def getAvailableVmID(
    proxmox_api_url : str,
    proxmox_api_node : str,
    proxmox_api_user : str,
    proxmox_api_user_password : str
) -> int:
    """ The global logic is to connect to the proxmox api so as to retrieve the next VM ID ready to use """

    response = requests.post(
        f"{proxmox_api_url}/access/ticket", 
        data={
            "username": proxmox_api_user,
            "password": proxmox_api_user_password
        }, 
        verify=False
    ).json()["data"]
    ticket = response["ticket"]

    use_ids = []
    for vm in ["lxc", "qemu"]:
        response = requests.get(
            f"{proxmox_api_url}/nodes/{proxmox_api_node}/{vm}", 
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

    return new_vm_id


def loadVars(
    yaml_file : str
) -> dict :
    """ The goal was to load variables defined inside 'yaml_file' """
    data = None
    
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    return data


def buildVmOnProxmox(
    DEPLOYMENT_STEPS : List[str],
    ip_4_set : str = None
) -> None:
    """ The goal was to build and create the infrastructure on Proxmox VE based on 'DEPLOYMENT_STEPS' """

    for step in range(len(DEPLOYMENT_STEPS)):
        # Save terraform_config_step to a file
        builder = DEPLOYMENT_STEPS[step]
        with open(f"main.tf", "w") as stream:
            stream.write(builder)
        #
        if ip_4_set and (step == 2):
            # wait until the vm boots
            while not ping(ip_4_set):
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] Waiting for yuor VM to be available on network <{ip_4_set}>...", end="")
                sleep(3)
            print(f"\r[{datetime.now().strftime('%H:%M:%S')}] Thy VM was now  available on network---")
            #
            print(tf.terraform_init_upgrade())
        else:
            print(tf.terraform_init())
        #
        # Building a step
        print(tf.terraform_apply(skip_plan=True))
        print(tf.terraform_output())


def getIP(
    text : str
):
    ip = None
    while True:
        try:
            ip = str(ipaddress.ip_address(input(text)))
        except KeyboardInterrupt:
            exit()
        except:
            continue
        else:
            break
    return ip


def getPassword(
    text : str
):
    password = None
    while True and (not password):
        try:
            password = getpass.getpass(text)
        except KeyboardInterrupt:
            exit()
        except:
            continue
        else:
            break
    return password


def getInput(
    text : str
):
    user_input = None
    while True and (not user_input):
        try:
            user_input = input(text)
        except KeyboardInterrupt:
            exit()
        except:
            continue
        else:
            break
    return user_input 


def getInteger(
    text : str
):
    user_input = None
    while True:
        try:
            user_input = int(input(text))
        except KeyboardInterrupt:
            exit()
        except:
            continue
        else:
            break
    return user_input 


def getBooInput(
    text : str
):
    user_input = None
    while True and (not user_input):
        try:
            user_input = input(text)

            if user_input in ['y', 'n']:
                break
        except KeyboardInterrupt:
            exit()
        except:
            continue
    return user_input == 'y' 