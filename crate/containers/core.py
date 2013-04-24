#!/usr/bin/env python
# Copyright (c) 2013 Evan Hazlett
#
import base

def get_script():
    """
    Returns the base cloud-init provisioning script for core container
    """
    tmpl = base.get_script()
    tmpl += """
echo "Provisioning in progress..." > /etc/motd.tail
install_core_packages
install_puppet

# start ntp -- doesn't seem to start on its own
service ntp start

"""
    return tmpl
