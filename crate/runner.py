#!/usr/bin/env python
# Copyright (c) 2013 Evan Hazlett
#
from argparse import ArgumentParser
import logging
import os
import sys
import core

# set logging levels
logging.getLogger('paramiko').setLevel(logging.ERROR)
logging.getLogger('ssh').setLevel(logging.ERROR)

def show_base_containers(**kwargs):
    c = core.CONTAINERS.keys()
    c.sort()
    print('\n'.join(c))

def run(**kwargs):
    log = logging.getLogger('main')
    cmd = kwargs.get('command')
    # convert to list
    hosts = kwargs.get('hosts', '').split(',')
    kwargs['hosts'] = hosts
    cnt = kwargs.get('base_containers')
    ssh_key = kwargs.get('public_key')
    password = kwargs.get('password')
    if cmd == 'create':
        if not ssh_key and not password:
            log.error('You must specify an SSH public key or password')
            sys.exit(1)
    if cnt:
        kwargs['base_containers'] = kwargs.get('base_containers','').split(',')
    # commands
    commands = {
        'create': core.create,
        'list': core.list_instances,
        'start': core.start,
        'info': core.info,
        'console': core.console,
        'stop': core.stop,
        'destroy': core.destroy,
        'clone': core.clone,
        'import': core.import_container,
        'export': core.export_container,
        'forward-port': core.forward_port,
        'list-ports': core.list_ports,
        'remove-port': core.remove_port,
        'set-memory-limit': core.set_memory_limit,
        'get-memory-limit': core.show_memory_limit,
        'set-cpu-limit': core.set_cpu_limit,
        'get-cpu-limit': core.show_cpu_limit,
        'list-base-containers': show_base_containers,
        'node': core.start_node,
    }
    if cmd in commands:
        commands[cmd](**kwargs)

def main():
    log = logging.getLogger('main')
    parser = ArgumentParser('crate')
    parser.add_argument('--debug', dest='debug', action='store_true',
        default=False, help='Show Debug')

    subs = parser.add_subparsers(dest='command')

    list_parser = subs.add_parser('list', description='')
    list_parser.add_argument('--all', action='store_true', default=True,
        help='Show all containers')

    list_base_containers_parser = subs.add_parser('list-base-containers',
        description='Show Base Containers')
    list_base_containers_parser.add_argument('--all', action='store_true',
        default=True, help='Show all base containers')

    info_parser = subs.add_parser('info', description='')
    info_parser.add_argument('-n', '--name', action='store',
        help='Container name')
    info_parser.add_argument('--all', action='store_true', default=True,
        help='Show container info')


    create_parser = subs.add_parser('create', description='')
    create_parser.add_argument('-n', '--name', action='store',
        help='Container name')
    create_parser.add_argument('-d', '--distro', action='store',
        default='ubuntu-cloud', help='Container distro name')
    create_parser.add_argument('-r', '--release', action='store', default='',
        help='Container distro release')
    create_parser.add_argument('-a', '--arch', action='store', default='',
        help='Container distro architecture')
    create_parser.add_argument('-f', '--user-data-file', action='store',
        help='Path or URL to user data file (ubuntu cloud images only)')
    create_parser.add_argument('-b', '--base-containers', action='store',
        default=None, help='Base containers (comma separated)')
    create_parser.add_argument('-s', '--public-key', action='store',
        help='Path or URL to SSH public key (ubuntu cloud images only)')
    create_parser.add_argument('-p', '--password', action='store',
        default=None,
        help='Ubuntu user password (ubuntu cloud init images only)')

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
    forward_port_parser.add_argument('-r', '--host-port', action='store',
        help='Host port for NAT')

    list_ports_parser = subs.add_parser('list-ports', description='')
    list_ports_parser.add_argument('-n', '--name', action='store',
        help='Container name')

    remove_port_parser = subs.add_parser('remove-port', description='')
    remove_port_parser.add_argument('-n', '--name', action='store',
        help='Container name')
    remove_port_parser.add_argument('-p', '--port', action='store',
        help='Container port')

    get_memory_parser = subs.add_parser('get-memory-limit', description='')
    get_memory_parser.add_argument('-n', '--name', action='store',
        help='Container name')

    set_memory_parser = subs.add_parser('set-memory-limit', description='')
    set_memory_parser.add_argument('-n', '--name', action='store',
        help='Container name')
    set_memory_parser.add_argument('-m', '--memory', action='store',
        help='Container memory limit (in MB)')

    get_cpu_parser = subs.add_parser('get-cpu-limit', description='')
    get_cpu_parser.add_argument('-n', '--name', action='store',
        help='Container name')

    set_cpu_parser = subs.add_parser('set-cpu-limit', description='')
    set_cpu_parser.add_argument('-n', '--name', action='store',
        help='Container name')
    set_cpu_parser.add_argument('-p', '--percent', action='store',
        help='Container CPU limit (in percent)')

    node_parser = subs.add_parser('node', description='')
    node_parser.add_argument('-s', '--start', action='store_true',
        default=False, help='Start LXC Create node')
    node_parser.add_argument('--redis-host', action='store',
        default='localhost', help='Crate API Redis Host')
    node_parser.add_argument('--redis-port',  action='store',
        type=int, default=6379, help='Crate API Redis Port')
    node_parser.add_argument('--redis-db',  action='store',
        type=int, default=0, help='Crate API Redis DB')
    node_parser.add_argument('--redis-password', action='store',
        default=None, help='Crate API Redis Password')
    node_parser.add_argument('--channel', action='store',
        default='crate', help='Crate API channel')

    args = parser.parse_args()
    # set log level
    if args.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level,
        format='%(levelname)-10s %(message)s')
    logging.getLogger('requests').setLevel(logging.ERROR)
    # main
    if not args.command:
        parser.print_help()
    else:
        try:
            run(**args.__dict__)
        except Exception, e:
            log.error(e)
            sys.exit(1)

if __name__=='__main__':
    main()
