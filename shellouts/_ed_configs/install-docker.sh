#!/bin/bash

apt-get update -y || exit 
#service lxcfs stop
#apt-get remove -y -q lxc-common lxcfs lxd lxd-client  
apt-get update -y 

apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common -y

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - || exit 1

apt-key fingerprint 0EBFCD88 || exit 1

add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable" || exit 1

apt-get update || exit 1
apt-get install docker-ce -y
