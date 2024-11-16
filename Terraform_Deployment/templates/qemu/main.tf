provider "proxmox" {
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

# resource "proxmox_vm_qemu" "test_vm" {
#     count       = 1
#     name        = var.vm_hostname
#     desc        = var.vm_description
#     target_node = var.pm_target_node

#     clone      = var.vm_ci_template
#     full_clone = true

#     network {
#       model     = "virtio"
#       bridge    = var.vm_bridge_interface
#       firewall  = true
#       link_down = false
#     }

#     ciuser       = var.vm_ci_user
#     cipassword   = var.vm_ci_password
#     sshkeys      = var.vm_ci_pubkey
#     ipconfig0    = var.vm_ci_netconf
#     searchdomain = var.vm_ci_domain
#     nameserver   = var.vm_ci_dnserv

#     scsihw  = "virtio-scsi-pci"
#     hotplug = "disk,network,usb"
#     cpu     = "x86-64-v2-AES"
#     kvm     = false
#     onboot  = true
    
#     cores    = var.vm_cores
#     bootdisk = "scsi0"
#     memory   = var.vm_memory
#     sockets  = 1

#     depends_on = [null_resource.resize_disk]
# }

## resource "null_resource" "execute_commands" {
##     provisioner "file" {
##         source      = "../../../config/ssham-key"
##         destination = "/root/ssham-key"
##     }

##     provisioner "file" {
##         source      = "../../../config/users"
##         destination = "/root/users"
##     }

##     provisioner "file" {
##         source      = "../../../config/users_groups"
##         destination = "/root/users_groups"
##     }

##     provisioner "file" {
##         source      = "../../../setup/.bashrc"
##         destination = "/root/.bashrc"
##     }

##     provisioner "file" {
##         source      = "../../../setup/zabbix_agent2.conf"
##         destination = "/root/zabbix_agent2.conf"
##     }

##     provisioner "file" {
##         source      = "../../../setup/systemd-timesyncd.service"
##         destination = "/root/systemd-timesyncd.service"
##     }

##     provisioner "file" {
##         source      = "../../../setup/timesyncd.conf"
##         destination = "/root/timesyncd.conf"
##     }

##     provisioner "remote-exec" {
##         script   = "../../../setup/main.sh"
##     }

##     connection {
##         type        = "ssh"
##         user        = "root"
##         host        = var.vm_ip_4_address
##         private_key = file(var.ssh_private_key_file)
##     }

##     depends_on = [proxmox_vm_qemu.test_vm[0]]
## }