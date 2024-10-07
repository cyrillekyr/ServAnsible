#!/bin/bash


echo "%dev ALL=(ALL) NOPASSWD: /usr/bin/su dev, /usr/bin/su - dev" > /etc/sudoers.d/config-sudo


echo "%sysadmin ALL=(ALL) NOPASSWD: /usr/bin/su sysadmin, /usr/bin/su - sysadmin" >> /etc/sudoers.d/config-sudo


echo "sysadmin ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/config-sudo


echo "Done !!!"
