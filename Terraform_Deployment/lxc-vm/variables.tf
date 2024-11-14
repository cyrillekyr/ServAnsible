variable "pm_api_url" {
    description = "The proxmox server API url"
    type        = string
}

variable "pm_user" {
    description = "The proxmox server username"
    type        = string
}

variable "pm_password" {
    description = "The proxmox server username's password"
    type        = string
}

variable "pm_target_node" {
    description = "The proxmox server name"
    type        = string
}

variable "vm_hostname" {
    description = "The VM hostname"
    type        = string
}

variable "vm_ct_template" {
    description = "The CT template name the VM will be built-on"
    type        = string
}

variable "vm_disk_size" {
    description = "The VM disk size"
    type        = string
    default     = "8G"
}

variable "vm_bridge_interface" {
    description = "The proxmox interface to wich the VM NIC will be bridged on"
    type        = string
}

variable "vm_ipv4_address" {
    description = "The proxmox VM NIC IPv4 address"
    type        = string
}

variable "vm_full_ipv4_address" {
    description = "The proxmox VM NIC IPv4 address followed by CIDR mask"
    type        = string
}

variable "vm_gw_ipv4_address" {
    description = "The proxmox VM gateway IPv4 address"
    type        = string
}

variable "vm_name_server" {
    description = "The DNS server IPv4 to set on VM"
    type        = string
    default     = "8.8.8.8"
}

variable "vm_search_domain" {
    description = "The domain name to set on VM"
    type        = string
    default     = "tettrix.infra"
}

variable "vm_cores" {
    description = "The number of CPU cores used by the VM"
    type        = number
}

variable "vm_memory" {
    description = "The RAM size used by the VM"
    type        = number
}

variable "vm_swap" {
    description = "The swap size used by the VM"
    type        = number
}

variable "vm_description" {
    description = "A description about the VM in state of deployment"
    type        = string
    default     = "Terraform-managed LXC container"
}

variable "ssh_public_key" {
    description = "SSH public key that will be used for remote access"
    type        = string
}

variable "ssh_private_key_file" {
    description = "Path to the file storing the SSH private key that will be used to remotely access the VM"
    type        = string
}