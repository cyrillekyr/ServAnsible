terraform {
  required_version = ">= 0.14"
  required_providers {
    proxmox = {
      source = "TheGameProfi/proxmox"
      version = "2.9.15"
    }
  }
}