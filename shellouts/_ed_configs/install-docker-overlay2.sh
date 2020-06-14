#!/bin/bash

apt-get update -y 
#service lxcfs stop
#apt-get remove -y -q lxc-common lxcfs lxd lxd-client
apt-get update -y 

apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
apt-add-repository 'deb https://apt.dockerproject.org/repo ubuntu-xenial main'
apt-get update -y 

apt-cache policy docker-engine
apt-get install -y --allow-unauthenticated docker-engine

systemctl stop docker
 
CONFIGURATION_FILE=$(systemctl show --property=FragmentPath docker | cut -f2 -d=)
cp $CONFIGURATION_FILE /etc/systemd/system/docker.service
 
perl -pi -e 's/^(ExecStart=.+)$/$1 -s overlay2/' /etc/systemd/system/docker.service
 
systemctl daemon-reload
systemctl start docker
