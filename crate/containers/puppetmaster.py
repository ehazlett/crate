#!/usr/bin/env python
# Copyright (c) 2013 Evan Hazlett
#
import base

def get_script():
    """
    Returns the base cloud-init provisioning script for Puppet Master

    """
    tmpl = base.get_script()
    tmpl += """
install_core_packages
install_puppet
install_packages "puppetmaster-passenger"

"""
    return tmpl
