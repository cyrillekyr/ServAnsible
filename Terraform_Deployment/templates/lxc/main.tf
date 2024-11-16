provider "proxmox" {
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
    password      = var.vm_root_password
    ostype        = "debian"

    rootfs {
        storage = "local-lvm"
        size    = var.vm_disk_size
    }
    
    network {
        name     = "eth0"
        bridge   = var.vm_bridge_interface
        ip       = var.vm_ip_4_scheme
        ip6      = "auto"
        # #gw       = var.vm_gw_ip_4
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
#         source      = "../../../config/ssham-key"
#         destination = "/root/ssham-key"
#     }

#     provisioner "file" {
#         source      = "../../../config/users"
#         destination = "/root/users"
#     }

#     provisioner "file" {
#         source      = "../../../config/users_groups"
#         destination = "/root/users_groups"
#     }

#     provisioner "file" {
#         source      = "../../../setup/.bashrc"
#         destination = "/root/.bashrc"
#     }

#     provisioner "file" {
#         source      = "../../../setup/zabbix_agent2.conf"
#         destination = "/root/zabbix_agent2.conf"
#     }

#     provisioner "file" {
#         source      = "../../../setup/systemd-timesyncd.service"
#         destination = "/root/systemd-timesyncd.service"
#     }

#     provisioner "file" {
#         source      = "../../../setup/timesyncd.conf"
#         destination = "/root/timesyncd.conf"
#     }

#     provisioner "remote-exec" {
#         script   = "../../../setup/main.sh"
#     }

#     connection {
#         type        = "ssh"
#         user        = "root"
#         host        = var.vm_ip_4_address
#         private_key = file(var.ssh_private_key_file)
#     }

#     depends_on = [proxmox_lxc.test_lxc_container[0]]
# }