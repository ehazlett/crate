#!/usr/bin/env python
# Copyright (c) 2013 Evan Hazlett
#
import base

def get_script():
    """
    Returns the base cloud-init provisioning script for ElasticSearch

    """
    tmpl = base.get_script()
    tmpl += """
install_core_packages
ES_DEB="/tmp/elasticsearch.deb"

wget "https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.20.6.deb" -O $ES_DEB
dpkg -i $ES_DEB
apt-get -f -y install
rm $ES_DEB

"""
    return tmpl
