#!/bin/sh

# update apt
apt-get -y update 2>&1 > /dev/null
apt-get -y install vim wget curl lxc yum btrfs-tools

# update rc.local
echo "iptables-restore /etc/crate.iptables\nexit 0" > /etc/rc.local

IP=`hostname -I | awk '{ print $1; }'`

echo "\nYour vagrant box should be available at $IP"
