#!/usr/bin/env python
# Copyright (c) 2013 Evan Hazlett
#
def get_script():
    """
    Returns the base cloud-init provisioning script for containers

    """
    tmpl = """#!/bin/bash
CORE_PKGS="wget curl python-dev python-setuptools libxml2-dev libxslt-dev vim git-core unzip"
MODULE_DIR=/opt/puppet

# core
apt-get update

function install_pkgs() {
    DEBIAN_FRONTEND=noninteractive apt-get -y install $*
}

install_pkgs $CORE_PKGS

easy_install pip
pip install virtualenv

# puppet
wget http://apt.puppetlabs.com/puppetlabs-release-`cat /etc/lsb-release |grep DISTRIB_CODENAME | awk -F'=' '{print $2}'`.deb -O /tmp/puppetlabs.deb
dpkg -i /tmp/puppetlabs.deb

apt-get update

install_pkgs puppet-common

git clone https://github.com/arcus-io/puppet.git $MODULE_DIR

"""
    return tmpl
