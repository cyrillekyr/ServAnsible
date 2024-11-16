variable "pm_api_url" {
    description = "The proxmox server API url"
    type        = string
    default     = ""
}

variable "pm_user" {
    description = "The proxmox server username"
    type        = string
    default     = ""
}

variable "pm_host_user" {
    description = "The proxmox server username with neither 'pam' nor 'pve'"
    type        = string
    default     = ""
}

variable "pm_host_ip" {
    description = "The proxmox server IP address"
    type        = string
    default     = ""
}

variable "pm_password" {
    description = "The proxmox server username's password"
    type        = string
    default     = ""
}

variable "pm_target_node" {
    description = "The proxmox server name"
    type        = string
    default     = ""
}

variable "vm_hostname" {
    description = "The VM hostname"
    type        = string
    default     = ""
}

variable "vm_ci_template" {
    description = "The CT template name the VM will be built-on"
    type        = string
    default     = ""
}

variable "vm_disk_size" {
    description = "The VM disk size"
    type        = string
    default     = "8G"
}

variable "vm_bridge_interface" {
    description = "The proxmox interface to wich the VM NIC will be bridged on"
    type        = string
    default     = ""
}

variable "vm_ip_4_address" {
    description = "The proxmox VM NIC IPv4 address"
    type        = string
    default     = ""
}

variable "vm_search_domain" {
    description = "The domain name to set on VM"
    type        = string
    default     = "tettrix.infra"
}

variable "vm_cores" {
    description = "The number of CPU cores used by the VM"
    type        = number
    default     = 0
}

variable "vm_memory" {
    description = "The RAM size used by the VM"
    type        = number
    default     = 0
}

variable "vm_description" {
    description = "A description about the VM in state of deployment"
    type        = string
    default     = "Terraform-managed LXC container"
}

variable "ssh_private_key_file" {
    description = "Path to the file storing the SSH private key that will be used to remotely access the VM"
    type        = string
    default     = ""
}

variable "vm_ci_template_id" {
    description = "The vm template ID based on wich the VM will be built"
    type        = string
    default     = ""
}

variable "vm_ci_user" {
    description = "The user to create at VM boot"
    type        = string
    default     = ""
}

variable "vm_ci_password" {
    description = "The password bound to that created user"
    type        = string
    default     = ""
}

variable "vm_ci_pubkey" {
    description = "The ssh public key bound to that created user"
    type        = string
    default     = ""
}

variable "vm_ci_netconf" {
    description = "The network configuration to apply to the VM at boot"
    type        = string
    default     = ""
}

variable "vm_ci_domain" {
    description = "The domain name to configure on the VM at boot"
    type        = string
    default     = ""
}

variable "vm_ci_dnserv" {
    description = "The DNS server IP address to configure on the VM at boot"
    type        = string
    default     = ""
}