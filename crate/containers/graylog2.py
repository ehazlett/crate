#!/usr/bin/env python
# Copyright (c) 2013 Evan Hazlett
#
import base

def get_script():
    """
    Returns the base cloud-init provisioning script for Graylog2

    """
    tmpl = base.get_script()
    tmpl += """
install_core_packages
install_puppet
cd $MODULE_DIR
puppet apply -e "include graylog2" --modulepath modules

"""
    return tmpl
