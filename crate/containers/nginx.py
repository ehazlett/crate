#!/usr/bin/env python
# Copyright (c) 2013 Evan Hazlett
#
import base

def get_script():
    """
    Returns the base cloud-init provisioning script for Nginx

    """
    tmpl = base.get_script()
    tmpl += """
cd $MODULE_DIR
puppet apply -e "include nginx" --modulepath modules

"""
    return tmpl
