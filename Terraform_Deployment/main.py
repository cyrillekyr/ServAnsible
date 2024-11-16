import os, shutil
from automation import utils, views, lxc_provision

proxmox_config = "Terraform_Deployment/vars/proxmox.yaml"

vm_type = "lxc" if views.main() == 1 else "qemu"
vm_config = f"Terraform_Deployment/vars/{vm_type}.yaml"

with open(proxmox_config, "w") as file:
    file.write(views.proxmox())

data = utils.loadVars(proxmox_config)

vm_id = utils.getAvailableVmID(
    proxmox_api_url=data['proxmox']['api_url'],
    proxmox_api_node=data['proxmox']['node'],
    proxmox_api_user=data['proxmox']['user']['name'],
    proxmox_api_user_password=data['proxmox']['user']['password']
)

working_dir = f"Terraform_Deployment/.deployed/{vm_type}-vm/{vm_id}"
os.makedirs(
    working_dir,
    exist_ok=True
)

with open(vm_config, "w") as file:
    if vm_type == "lxc":
        file.write(views.lxc(
            proxmox_node=data['proxmox']['node'],
            working_dir=working_dir,
            vm_id=vm_id
        ))
    elif vm_type == "qemu":
        file.write(views.qemu(
            proxmox_node=data['proxmox']['node'],
            working_dir=working_dir,
            vm_id=vm_id
        ))

data.update(utils.loadVars(vm_config))

shutil.move("Terraform_Deployment/vars/proxmox.yaml", f"Terraform_Deployment/{working_dir}/proxmox.yaml")
shutil.move(f"Terraform_Deployment/vars/{vm_type}.yaml", f"Terraform_Deployment/{working_dir}/{vm_type}.yaml")
shutil.copy("Terraform_Deployment/templates/provider.tf", f"Terraform_Deployment/{working_dir}/provider.tf")
shutil.copy(f"Terraform_Deployment/templates/{vm_type}/variables.tf", f"Terraform_Deployment/{working_dir}/variables.tf")

# Define the Terraform configuration
with open(f"Terraform_Deployment/templates/{vm_type}/main.tf", "r") as file:
    terraform_config = file.read()

if vm_type == "lxc":
    lxc_provision.run(
        terraform_config=terraform_config,
        working_dir=working_dir,
        data=data
    )
elif vm_type == "qemu":
    qemu_provision.run(
        terraform_config=terraform_config,
        working_dir=working_dir,
        data=data
    )
