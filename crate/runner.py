#!/usr/bin/env python
# Copyright (c) 2013 Evan Hazlett
#
from argparse import ArgumentParser
from fabric.api import execute, env
import fabric.state
import logging
import os
import sys
import core

fabric.state.output['running'] = False
env.output_prefix = False
# set logging levels
logging.getLogger('paramiko').setLevel(logging.ERROR)

def run(**kwargs):
    cmd = kwargs.get('command')
    env.user = kwargs.get('user')
    env.key_filename = kwargs.get('key_filename')
    # convert to list
    hosts = kwargs.get('hosts', '').split(',')
    kwargs['hosts'] = hosts
    # commands
    commands = {
        'create': core.create,
        'list': core.list,
        'start': core.start,
        'console': core.console,
        'stop': core.stop,
        'destroy': core.destroy,
        'clone': core.clone,
        'import': core.import_container,
        'export': core.export_container,
        'forward-port': core.forward_port,
        'list-ports': core.list_ports,
        'remove-port': core.remove_port,
    }
    if cmd in commands:
        execute(commands[cmd], **kwargs)

def main():
    parser = ArgumentParser('crate')
    parser.add_argument('-H', '--hosts', dest='hosts', required=True,
        default='127.0.0.1', help='Hosts (comma separated)')
    parser.add_argument('-i', '--key', dest='key_filename',
        help='SSH private key')
    parser.add_argument('-u', '--user', dest='user',
        help='SSH user')
    parser.add_argument('--debug', dest='debug', action='store_true',
        default=False, help='Show Debug')

    subs = parser.add_subparsers(dest='command')

    list_parser = subs.add_parser('list', description='')
    list_parser.add_argument('--all', action='store_true', default=True,
        help='Show all containers')

    create_parser = subs.add_parser('create', description='')
    create_parser.add_argument('-n', '--name', action='store',
        help='Container name')
    create_parser.add_argument('--distro', action='store', default='',
        help='Container distro name')
    create_parser.add_argument('--release', action='store', default='',
        help='Container distro release')
    create_parser.add_argument('--arch', action='store', default='',
        help='Container distro architecture')

    destroy_parser = subs.add_parser('destroy', description='')
    destroy_parser.add_argument('-n', '--name', action='store',
        help='Container name')

    start_parser = subs.add_parser('start', description='')
    start_parser.add_argument('-n', '--name', action='store',
        help='Container name')
    start_parser.add_argument('--ephemeral', action='store_true', default=False,
        help='Start ephemeral container')

    console_parser = subs.add_parser('console', description='')
    console_parser.add_argument('-n', '--name', action='store',
        help='Container name')

    stop_parser = subs.add_parser('stop', description='')
    stop_parser.add_argument('-n', '--name', action='store',
        help='Container name')

    clone_parser = subs.add_parser('clone', description='')
    clone_parser.add_argument('-n', '--name', action='store',
        help='Container name')
    clone_parser.add_argument('-s', '--source', action='store',
        help='Source container name')
    clone_parser.add_argument('--size', action='store', default='2',
        help='Container size in GB (default: 2)')

    export_parser = subs.add_parser('export', description='')
    export_parser.add_argument('-n', '--name', action='store',
        help='Container name')

    import_parser = subs.add_parser('import', description='')
    import_parser.add_argument('-n', '--name', action='store',
        help='Container name')
    import_parser.add_argument('--local-path', action='store',
        help='Path to exported container (.tar.gz)')

    console_parser = subs.add_parser('console', description='')
    console_parser.add_argument('-n', '--name', action='store',
        help='Container name')

    forward_port_parser = subs.add_parser('forward-port', description='')
    forward_port_parser.add_argument('-n', '--name', action='store',
        help='Container name')
    forward_port_parser.add_argument('-p', '--port', action='store',
        help='Container port')

    list_ports_parser = subs.add_parser('list-ports', description='')
    list_ports_parser.add_argument('-n', '--name', action='store',
        help='Container name')

    remove_port_parser = subs.add_parser('remove-port', description='')
    remove_port_parser.add_argument('-n', '--name', action='store',
        help='Container name')
    remove_port_parser.add_argument('-p', '--port', action='store',
        help='Container port')

    args = parser.parse_args()
    # set log level
    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level,
        format='%(asctime)s %(levelname)s: %(message)s')
    logging.getLogger('requests').setLevel(logging.ERROR)
    # main
    if not args.command:
        parser.print_help()
    else:
        run(**args.__dict__)

if __name__=='__main__':
    main()
