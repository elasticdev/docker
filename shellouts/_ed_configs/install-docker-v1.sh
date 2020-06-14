#!/bin/bash

apt-get update -y 
#service lxcfs stop
#apt-get remove -y -q lxc-common lxcfs lxd lxd-client
apt-get update -y 

apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D

export LSB_RELEASE=`cat /etc/lsb-release |grep DISTRIB_CODENAME|cut -d "=" -f 2`
apt-add-repository "deb https://apt.dockerproject.org/repo ubuntu-${LSB_RELEASE} main"
apt-get update -y || exit 1
apt-cache policy docker-engine || exit 1
apt-get install -y --allow-unauthenticated docker-engine
