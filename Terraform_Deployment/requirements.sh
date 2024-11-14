#/bin/bash

sudo apt install --reinstall software-properties-common # solve issue often raised by "add-apt-repository"

# here comes terraform's installation process [found on doc (https://developer.hashicorp.com/terraform/install)]
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=$(dpkg --print-architecture)] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt update && sudo apt install terraform

pip install paramiko ping3 # "paramiko" allows us to generate RSA key pair
