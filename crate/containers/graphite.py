#!/usr/bin/env python
# Copyright (c) 2013 Evan Hazlett
#
import base

def get_script():
    """
    Returns the base cloud-init provisioning script for Graphite

    """
    tmpl = base.get_script()
    tmpl += """
cd $MODULE_DIR
puppet apply -e "include graphite" --modulepath modules

"""
    return tmpl
