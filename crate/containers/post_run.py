#!/usr/bin/env python
# Copyright (c) 2013 Evan Hazlett
#

def get_script():
    """
    Returns the base cloud-init provisioning script for core container
    """
    tmpl = """
# remove motd message
rm /etc/motd.tail

"""
    return tmpl
