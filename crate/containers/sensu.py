#!/usr/bin/env python
# Copyright (c) 2013 Evan Hazlett
#
import base

def get_script():
    """
    Returns the base cloud-init provisioning script for Sensu

    """
    tmpl = base.get_script()
    tmpl += """
install_core_packages
install_puppet
cd $MODULE_DIR
puppet apply -e "include sensu::server" --modulepath modules

# restart sensu as puppet starts but it exits ; need to debug
service sensu-api start
service sensu-server start
service sensu-dashboard start
service sensu-client start

"""
    return tmpl
