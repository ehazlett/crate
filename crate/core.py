from datetime import date
import os
import tempfile
import random
import string
import containers
import requests
import logging
from redis import Redis
import subprocess
import socket
import simplejson as json
import re

# TODO: parse lxc config to get path
LXC_PATH = '/var/lib/lxc'
# this script returns the lxc guest IP
# (from Canonical -- see file header for more)
LXC_IP_LINK = 'https://gist.github.com/ehazlett/5274446/raw/070f8a77f7f5738ee2d855a1b94e2e9a23d770c6/gistfile1.txt'

log = logging.getLogger('core')

CONTAINERS = {
    'apache2': containers.apache2.get_script,
    'core': containers.core.get_script,
    'elasticsearch': containers.elasticsearch.get_script,
    'graphite': containers.graphite.get_script,
    'graylog2': containers.graylog2.get_script,
    'haproxy': containers.haproxy.get_script,
    'memcached': containers.memcached.get_script,
    'mongodb': containers.mongodb.get_script,
    'mysql': containers.mysql.get_script,
    'nginx': containers.nginx.get_script,
    'openresty': containers.openresty.get_script,
    'postgres': containers.postgres.get_script,
    'post_run': containers.post_run.get_script,
    'puppetdb': containers.puppetdb.get_script,
    'puppetmaster': containers.puppetmaster.get_script,
    'puppetdashboard': containers.puppetdashboard.get_script,
    'rabbitmq': containers.rabbitmq.get_script,
    'redis': containers.redis.get_script,
    'sentry': containers.sentry.get_script,
    'sensu': containers.sensu.get_script,
    'solr': containers.solr.get_script,
    'uwsgi': containers.uwsgi.get_script,
}

def _run_command(cmd=None):
    p = subprocess.Popen([cmd], stdout=subprocess.PIPE,
        shell=True)
    out, err = p.communicate()
    return out

def get_lxc_ip(name=None):
    # get lxc-ip script if doesn't exist
    if not os.path.exists('/usr/local/bin/lxc-ip'):
            _run_command('wget {0} -O /usr/local/bin/lxc-ip ; chmod +x /usr/local/bin/lxc-ip'.format(
                LXC_IP_LINK))
    out = _run_command('/usr/local/bin/lxc-ip -n {0}'.format(name))
    return out.strip()

def create(name=None, distro='ubuntu-cloud', release='', arch='',
    user_data_file=None, base_containers=None, public_key=None,
    password=None, **kwargs):
    """
    Creates a new Container

    :param name: Name of container
    :param distro: Name of base distro (default: ubuntu-cloud)
    :param release: Name of base distro release
    :param arch: Architecture of container
    :param user_data_file: Path to user data file for cloud-init
        (ubuntu cloud images only)
    :param base_containers: Base Containers (ignores user_data_file)
    :param public_key: SSH public key for container
    :param password: Password for 'ubuntu' user (ubuntu cloud init only)

    """
    if not name:
        raise StandardError('You must specify a name')
    log.info('Creating {0}'.format(name))
    log.debug('Creating container {0}: Distro: {1} Version: {2}'.format(name,
        distro or 'default', release or 'default'))
    cmd = 'lxc-create -n {0} -t {1}'.format(name, distro)
    # everything below is for template options
    cmd += ' --'
    if arch:
        cmd += ' -a {0}'.format(arch)
    if release:
        cmd += ' -r {0}'.format(release)
    tmp_files = []
    if distro == 'ubuntu-cloud' and user_data_file or base_containers:
        if base_containers:
            for c in base_containers:
                if c not in CONTAINERS.keys():
                    raise StandardError('Unknown base container: {0}'.format(c))
            log.info('Provisioning with base container(s): {0}'.format(
                ', '.join(base_containers)))
            user_data_file = tempfile.mktemp()
            with open(user_data_file, 'w') as f:
                for c in base_containers:
                    f.write(CONTAINERS[c]())
                f.write(CONTAINERS['post_run']())
        else:
            # check for remote file
            if user_data_file.startswith('http'):
                tfile = tempfile.mktemp()
                with open(tfile, 'w') as f:
                    r = requests.get(user_data_file)
                    f.write(r.content)
                user_data_file = tfile
            elif not os.path.exists(user_data_file):
                raise StandardError('User data file must exist')
            log.debug('Provisioning with cloud-init file {0}'.format(
                user_data_file))
        # create user data file for use with lxc-create
        tmp_file = tempfile.mktemp()
        tmp_files.append(tmp_file)
        # change ubuntu password since ubuntu-cloud has no password
        # therefore console doesn't work
        if password:
            log.debug('Setting password')
            _run_command(r"sed -i '2s/^/echo ubuntu:{0} | chpasswd \n/' {1}".format(
                password, tmp_file))
        cmd += ' -u {0}'.format(tmp_file)
    if password and distro == 'ubuntu-cloud' and not user_data_file:
        log.debug('Setting password...')
        t = tempfile.mktemp()
        with open(t, 'w') as f:
            scr = '#!/bin/sh\necho ubuntu:{0} | chpasswd \n'.format(
                password)
            f.write(scr)
        tmp_files.append(t)
        cmd += ' -u {0}'.format(t)
    # check for public key
    if public_key:
        log.debug('Using custom SSH key')
        if public_key.startswith('http'):
            tfile = tempfile.mktemp()
            with open(tfile, 'w') as f:
                r = requests.get(public_key)
                f.write(r.content)
            public_key = tfile
        elif not os.path.exists(public_key):
            raise StandardError('SSH public key file must exist')
        # create remote user data file for use with lxc-create
        cmd += ' -S {0}'.format(public_key)
    log.info('Building')
    _run_command(cmd)
    # cleanup
    for f in tmp_files:
        if os.path.exists(f):
            os.remove(f)
    log.info('{0} created'.format(name))

#@task
def export_container(name=None, **kwargs):
    """
    Exports (tarball) specified container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    # TODO: parse config to get path
    export_name = '{0}-{1}.tar.gz'.format(name, date.today().isoformat())
    tmp_file = os.path.join('/tmp', export_name)
    log.info('Creating archive...')
    with cd(os.path.join(LXC_PATH, name)), hide('stdout'):
        sudo('tar czf {0} .'.format(tmp_file))
    log.info('Downloading {0} ...'.format(export_name))
    get(tmp_file, export_name)
    sudo('rm -f {0}'.format(tmp_file))

#@task
def import_container(name=None, local_path=None, **kwargs):
    """
    Imports a container from an export

    :param name: Name of container
    :param local_path: Path to exported container (tarball)

    """
    if not name or not os.path.exists(local_path):
        raise StandardError('You must specify a name and file must exist')
    tmp_file = '/tmp/{0}.tar.gz'.format(name)
    log.info('Uploading archive...')
    put(local_path, tmp_file)
    dest_path = os.path.join(LXC_PATH, name)
    sudo('mkdir -p {0}'.format(dest_path))
    log.info('Extracting...')
    with cd(dest_path), hide('stdout'):
        sudo('tar xzf {0} .'.format(tmp_file))
        # fix names
        config = run('cat {0}/config'.format(dest_path)).splitlines()
        new_conf = []
        utsname = None
        for l in config:
            if l.find('lxc.utsname') > -1:
                utsname = l.split('=')[-1].strip()
                l = 'lxc.utsname = {0}'.format(name)
            if l.find('lxc.mount') > -1:
                l = l.replace(utsname, name)
            if l.find('lxc.rootfs') > -1:
                l = l.replace(utsname, name)
            new_conf.append(l)
        with open('.tmpconf', 'w') as f:
            f.write('\n'.join(new_conf))
        put('.tmpconf', os.path.join(dest_path, 'config'), use_sudo=True)
        os.remove('.tmpconf')
    sudo('rm -f {0}'.format(tmp_file))
    log.info('Imported {0} successfully...'.format(name))

#@task
def list_instances(**args):
    """
    List all Containers

    """
    instances = get_instances()
    for k,v in instances.iteritems():
        log.info('{0:20} {1}'.format(k, v))

def start(name=None, ephemeral=False, environment=None, **kwargs):
    """
    Starts a Container

    :param name: Name of container
    :param ephemeral: Disregard changes after stop (default: False)
    :param environment: Environment variables (list of KEY=VALUE strings)

    """
    if not name:
        raise StandardError('You must specify a name')
    cmd = 'lxc-start -n {0} -c /tmp/{0}.lxc.console'.format(name)
    if ephemeral:
        cmd = 'lxc-start-ephemeral -o {0}'.format(name)
    if environment:
        container_env = os.path.join(LXC_PATH, name, 'rootfs/etc/environment')
        env = '\n'.join(environment)
        _run_command('echo \"{0}\" >> {1}'.format(env, container_env))
    _run_command('{0} -d > /dev/null 2>&1'.format(cmd))
    log.info('{0} started'.format(name))

#@task
def console(name=None, **kwargs):
    """
    Connects to Container console

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    open_shell('sudo lxc-console -e b -n {0} ; exit'.format(name))

def stop(name=None, **kwargs):
    """
    Stops a Container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    _run_command('lxc-stop -n {0}'.format(name))
    log.info('{0} stopped'.format(name))

def destroy(name=None, **kwargs):
    """
    Destroys a Container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    _run_command('lxc-destroy -n {0} -f'.format(name))
    log.info('{0} destroyed'.format(name))

def get_container_ports(name=None):
    if not name:
        raise StandardError('You must specify a name')
    # get ip of container
    container_ip = get_lxc_ip(name)
    # only show tcp to prevent duplicates for udp
    cur = _run_command('iptables -L -n -t nat | grep {0} | grep tcp'.format(
        container_ip))
    ports = {}
    if cur:
        for l in cur.splitlines():
            if l:
                dport = int(l.split()[-2].split(':')[1])
                target = int(l.split()[-1].split(':')[-1])
                ports[dport] = target
    return ports

#@task
def list_ports(name=None, **kwargs):
    """
    Removes a container port forward

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    ports = get_container_ports(name)
    for k,v in ports.iteritems():
        log.info('Port: {0} Target: {1}'.format(k,v))

#@task
def show_memory_limit(name=None, **kwargs):
    """
    Shows memory limit for a Container

    :param name: Name of container

    """
    mem = get_memory_limit(name)
    if mem == 0:
        limit = 'Unlimited'
    else:
        limit = '{0}MB'.format(mem)
    log.info('Memory limit for {0}: {1}'.format(name, limit))
    return limit

#@task
#@task
def show_cpu_limit(name=None, **kwargs):
    """
    Gets CPU limit for a Container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    limit = get_cpu_limit(name)
    log.info('CPU limit for {0}: {1}%'.format(name, limit))
    return limit

#@task
def info(name=None, **kwargs):
    """
    Shows current LXC info

    """
    instances = get_instances(name)
    for k,v in instances.iteritems():
        name = k
        state = v
        cpu = 'n/a'
        mem = 'n/a'
        ports = 'n/a'
        if state == 'running':
            with hide('stdout'):
                cpu = '{0}%'.format(get_cpu_limit(name))
                mem = get_memory_limit(name)
                c_ports = get_container_ports(name)
                if c_ports:
                    ports = ''
                for k,v in c_ports.iteritems():
                    ports += '{0}->{1} '.format(k,v)
                if mem == 0:
                    #mem = u"\u221E".encode('utf8')
                    mem = 'unlimited'
                else:
                    mem = '{0}M'.format(mem)
        log.info('{0:20} State: {1:8} CPU: {2:<4} RAM: {3:<12} Ports: {4}'.format(
            name, state, cpu, mem, ports))

def node_listen(redis_client=None, channel=None):
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)
    for msg in pubsub.listen():
        node_handle(msg, redis_client, channel)

def publish(data=None, action=None, msg_id=None, redis_client=None,
    channel=None):
    resp_data = {}
    resp_data['response'] = data
    resp_data['node'] = socket.getfqdn()
    resp_data['action'] = action
    resp_data['target'] = 'master'
    resp_data['id'] = msg_id
    redis_client.publish(channel, json.dumps(resp_data))

def node_handle(msg, redis_client=None, channel=None):
    if msg.get('type') == 'message':
        try:
            msg_data = json.loads(msg.get('data'))
            if msg_data.get('target') != 'node':
                return
            log.debug(msg)
            data = msg_data.get('data')
            handlers = {
                'get_containers': get_containers,
                'start_container': start,
                'stop_container': stop,
                'destroy_container': destroy,
                'create_container': create,
                'update_container': update_container,
                'clone_container': clone,
            }
            cmd = msg_data.get('action')
            if cmd in handlers.keys():
                resp_data = handlers[cmd](**data)
                publish(resp_data, cmd, msg_data.get('id'),
                    redis_client, channel)
        except Exception, e:
            import traceback
            traceback.print_exc()
            log.warning('Error parsing message: {0}'.format(e))

def start_node(**kwargs):
    log.info('Starting Crate Node')
    host = kwargs.get('redis_host')
    port = kwargs.get('redis_port')
    db = kwargs.get('redis_db')
    password = kwargs.get('redis_password')
    channel = kwargs.get('channel')
    rds = Redis(host=host, port=port, db=db, password=password)
    try:
        node_listen(rds, channel)
    except KeyboardInterrupt:
        log.info('Shutting down')

def get_containers(name=None):
    """
    Returns instances and state

    """
    o = _run_command('lxc-ls')
    instances = []
    if o.strip() != '':
        conts = o.split()
        for i in set(conts):
            instance_name = i.strip()
            if instance_name and not name or name and instance_name == name:
                info = {}
                info['name'] = instance_name
                ports = []
                cpu = 0
                mem = 0
                state = 'stopped'
                # check if running by looking for rootfs.hold (since lxc-ls
                #   output is ridiculous
                cgroup_path = '/sys/fs/cgroup/cpu/lxc'
                cgroup_container_path = '/sys/fs/cgroup/cpu/lxc/{0}'.format(
                    instance_name)
                if os.path.exists(cgroup_path) and os.path.exists(
                    cgroup_container_path):
                    state = 'running'
                    cpu = get_cpu_limit(instance_name)
                    mem = get_memory_limit(instance_name)
                    ports = get_container_ports(instance_name)
                info['state'] = state
                info['cpu'] = cpu
                info['memory'] = mem
                info['ports'] = ports
                info['node'] = socket.getfqdn()
                instances.append(info)
    return instances

def get_cpu_limit(name=None):
    """
    Gets cpu limit for a Container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    try:
        out = _run_command('lxc-cgroup -n {0} cpu.shares'.format(name))
        limit = int((float(int(out)) / float(1024)) * 100)  # convert to percent
    except:
        limit = 0
    return limit

def get_memory_limit(name=None):
    """
    Gets memory limit for a Container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    try:
        out = _run_command('lxc-cgroup -n {0} memory.limit_in_bytes'.format(name))
        mem = (int(out) / 1048576) # convert from bytes to MB
        if mem >= 1048576 * 1048576:
            mem = 0
    except:
        mem = 0
    return mem

def set_cpu_limit(name=None, percent=100, **kwargs):
    """
    Sets cpu limit for a Container

    :param name: Name of container
    :param percent: CPU priority in percent

    """
    if not name:
        raise StandardError('You must specify a name')
    log.info('Setting {0} CPU ratio to {1}%'.format(name, percent))
    # default cpu shares value is 1024
    ratio = int(1024 * (float(percent) / float(100)))
    _run_command('lxc-cgroup -n {0} cpu.shares {1}'.format(name, ratio))

def set_memory_limit(name=None, memory=256, **kwargs):
    """
    Sets memory limit for a Container

    :param name: Name of container
    :param memory: Max memory for container

    """
    if not name:
        raise StandardError('You must specify a name')
    mem = (int(memory) * 1048576) # convert from MB to Bytes
    # error happens when trying to assign to 0 ; set to very high limit
    if mem == 0:
        mem = int(1048576**3)
        memory = 'unlimited'
    else:
        memory = '{0}MB'.format(memory)
    log.info('Setting {0} memory limit to {1}'.format(name, memory))
    _run_command('lxc-cgroup -n {0} memory.limit_in_bytes {1}'.format(
        name, mem))

def forward_port(name=None, port=None, host_port=None, **kwargs):
    """
    Forwards a host port to a container port

    :param name: Name of container
    :param port: Port on container
    :param host_port: Host port

    """
    dport = host_port
    if not host_port:
        # find open port on host
        while True:
            dport = random.randint(10000, 50000)
            out = _run_command('netstat -lnt | awk \'$6 == "LISTEN" && $4 ~ ".{0}"\''.format(
                dport))
            if out == '':
                break
    # get ip of container
    container_ip = get_lxc_ip(name)
    _run_command('iptables -t nat -A PREROUTING -p tcp --dport {0} ' \
        '-j DNAT --to-destination {1}:{2}'.format(dport, container_ip,
        port))
    _run_command('iptables -t nat -A PREROUTING -p udp --dport {0} ' \
        '-j DNAT --to-destination {1}:{2}'.format(dport, container_ip,
        port))
    # save rules
    _run_command('iptables-save > /etc/crate.iptables')
    log.info('Service available for port {0} on host port {1}'.format(
        port, dport))

def remove_port(name=None, port=None, **kwargs):
    """
    Removes a container port forward

    :param name: Name of container
    :param port: Port on container

    """
    if not name:
        raise StandardError('You must specify a name')
    # get ip of container
    container_ip = get_lxc_ip(name)
    cur = _run_command('iptables -L -t nat | grep {0} | grep tcp'.format(
        container_ip))
    if cur:
        dport = cur.split()[-2].split(':')[1]
        _run_command('iptables -t nat -D PREROUTING -p tcp --dport {0} ' \
            '-j DNAT --to-destination {1}:{2}'.format(dport, container_ip,
            port))
        _run_command('iptables -t nat -D PREROUTING -p udp --dport {0} ' \
            '-j DNAT --to-destination {1}:{2}'.format(dport, container_ip,
            port))
        # save rules
        _run_command('iptables-save > /etc/crate.iptables')
        log.info('Forward for port {0} removed'.format(port))

def update_container(name=None, cpu=None, memory=None, ports=None, **kwargs):
    """
    Updates container ports and constraints

    """
    if not name:
        raise StandardError('You must specify a name')
    if cpu != None:
        set_cpu_limit(name, cpu)
    if memory != None:
        set_memory_limit(name, memory)
    existing_ports = list(get_container_ports(name).values())
    # the following check for list vs. dict is needed to handle
    # both types of input (server select port or user specified port)
    if ports != None:
        if isinstance(ports, list):
            for port in ports:
                if port not in existing_ports:
                    forward_port(name, port)
                    existing_ports.append(port)
        elif isinstance(ports, dict):
            for k,v in ports.iteritems():
                if k not in existing_ports:
                    forward_port(name, v, k)
                    existing_ports.append(v)
        # cleanup removed ports
        [remove_port(name, port) for port in existing_ports if \
            isinstance(ports, list) and port not in ports]
        [remove_port(name, port) for port in existing_ports if \
            isinstance(ports, dict) and port not in ports.values()]

def clone(name=None, source=None, size=2, **kwargs):
    """
    Creates a new Container

    :param name: Name of new container
    :param source: Name of source container
    :param size: Size of new container (in GB, default: 2)

    """
    if not name or not source:
        raise StandardError('You must specify a name and source')
    log.info('Cloning {0} to {1}'.format(source, name))
    _run_command('lxc-clone -o {0} -n {1} -s {2}G'.format(source, name, size))
    log.info('{0} created'.format(name))

