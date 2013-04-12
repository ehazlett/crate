#!/usr/bin/env python
# Copyright (c) 2013 Evan Hazlett
#
def get_script():
    """
    Returns the base cloud-init provisioning script for containers

    """
    tmpl = """#!/bin/bash
CORE_PKGS="wget curl collectd ntp python-dev python-setuptools libxml2-dev libxslt-dev vim git-core unzip"
MODULE_DIR=/opt/puppet

# core
apt-get update

function install_packages() {
    DEBIAN_FRONTEND=noninteractive apt-get -y install $*
}

# puppet
function install_puppet() {
    wget http://apt.puppetlabs.com/puppetlabs-release-`cat /etc/lsb-release |grep DISTRIB_CODENAME | awk -F'=' '{print $2}'`.deb -O /tmp/puppetlabs.deb
    dpkg -i /tmp/puppetlabs.deb

    apt-get update

    install_packages puppet-common
    git clone https://github.com/arcus-io/puppet.git $MODULE_DIR
}

function install_core_packages() {
    install_packages $CORE_PKGS
    easy_install pip
    pip install virtualenv
}

"""
    return tmpl
