#!/bin/bash

set -ex

# Function to add users
add_users() {
    echo "Adding users..."
    cat /root/users | while read user
    do
        echo "Adding user: $user"
        useradd -m "$user" || echo "User $user already exists."
    done
}

# Function to add users to groups
add_users_to_groups() {
    echo "Adding users to groups"
    awk -F' ' '{ if ($0 !~ /^\[.*\]$/ && $0 !~ /^[[:space:]]*$/) { system("echo Adding user " $1 " to groups: " $2 "; usermod -aG " $2 " " $1) } }' /root/users_groups
}

# Function to copy and execute change_shell.sh script
change_shell() {
    echo "Changing shell for all users"
    ls /home | while read result
    do
            usermod -s /bin/bash $result
            echo " Done for user $result "
    done
}

# Function to install sudo
install_sudo() {
    echo "Installing sudo..."
    apt-get update
    apt-get install -y sudo
}

# Function to set up sudo rights
setup_sudo_rights() {
    echo "Setting sudo rights for groups..."

    echo "%dev ALL=(ALL) NOPASSWD: /usr/bin/su dev, /usr/bin/su - dev" > /etc/sudoers.d/config-sudo
    echo "%sysadmin ALL=(ALL) NOPASSWD: /usr/bin/su sysadmin, /usr/bin/su - sysadmin" >> /etc/sudoers.d/config-sudo
    echo "sysadmin ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/config-sudo
}

# Function to install Zabbix Agent 2
install_zabbix_agent() {
    echo "Installing Zabbix Agent 2..."
    apt-get update
    apt-get install -y zabbix-agent2
    
    echo "Starting and enabling Zabbix Agent 2 service"
    systemctl start zabbix-agent2
    systemctl enable zabbix-agent2
}

# Function for SSHAM deployment
deploy_ssham() {
    echo "Copying ssham-key to .ssh/authorized_keys for all users"
    sshamkey=`cat /root/ssham-key`
    ls /home | while read result
    do
            mkdir /home/$result/.ssh
            chown $result:$result /home/$result/.ssh
            echo $sshamkey >>/home/$result/.ssh/authorized_keys
            chown $result:$result /home/$result/.ssh/authorized_keys
            echo " Done for user $result "
    done
    echo $sshamkey >>/root/.ssh/authorized_keys
    echo " Done for user root "
}

# Function to improve bashrc
improve_bashrc() {
    echo "Modifying each user .bashrc file"
    ls /home | while read result
    do
            cp /root/.bashrc /home/$result/.bashrc
            echo " Done for user $result "
    done
}

# Function to permit non-root to execute ping
permit_ping() {
    echo "Allowing non-root users to execute ping"
    setcap cap_net_raw+p /usr/bin/ping
}

# Function to install systemd-timesyncd
install_timesyncd() {
    echo "Installing systemd-timesyncd..."
    apt-get update
    apt-get install -y systemd-timesyncd
}

# Function to ensure systemd-timesyncd is started and enabled
start_enable_timesyncd() {
    echo "Ensuring systemd-timesyncd service is started and enabled..."
    systemctl start systemd-timesyncd
    systemctl enable systemd-timesyncd
}

# Function to reload the systemd daemon
reload_daemon() {
    echo "Reloading the systemd daemon..."
    systemctl daemon-reload
}

# Function to enable NTP
enable_ntp() {
    echo "Enabling NTP..."
    timedatectl set-ntp true
}

# Function to set the timezone
set_timezone() {
    local timezone="$1"
    echo "Setting timezone to $timezone..."
    timedatectl set-timezone "$timezone"
}

# Function to restart systemd-timesyncd
restart_timesyncd() {
    echo "Restarting systemd-timesyncd..."
    systemctl restart systemd-timesyncd
}

# Main script execution
add_users
add_users_to_groups
change_shell
install_sudo
setup_sudo_rights
install_zabbix_agent
deploy_ssham
improve_bashrc
permit_ping
mv /root/zabbix_agent2.conf /etc/zabbix/zabbix_agent2.conf

systemctl restart zabbix-agent2
install_timesyncd
start_enable_timesyncd
mv /root/systemd-timesyncd.service /lib/systemd/system/systemd-timesyncd.service
mv /root/timesyncd.conf /etc/systemd/timesyncd.conf

reload_daemon
enable_ntp
set_timezone "Africa/Porto-Novo"
restart_timesyncd
rm -rf /root/main.sh /root/users /root/users_groups

# echo "All tasks completed successfully."

reboot -h now
