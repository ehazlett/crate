from fabric.api import run, sudo, task, get, put, open_shell
from fabric.context_managers import cd, hide
from datetime import date
import os
import tempfile
import random
import string
import containers

# TODO: parse lxc config to get path
LXC_PATH = '/var/lib/lxc'
LXC_IP_LINK = 'https://gist.github.com/ehazlett/5274446/raw/070f8a77f7f5738ee2d855a1b94e2e9a23d770c6/gistfile1.txt'

CONTAINERS = {
    'apache2': containers.apache2.get_script,
    'core': containers.core.get_script,
    'graphite': containers.graphite.get_script,
    'memcached': containers.memcached.get_script,
    'mongodb': containers.mongodb.get_script,
    'mysql': containers.mysql.get_script,
    'nginx': containers.nginx.get_script,
    'puppetdb': containers.puppetdb.get_script,
    'puppetmaster': containers.puppetmaster.get_script,
    'puppetdashboard': containers.puppetdashboard.get_script,
    'rabbitmq': containers.rabbitmq.get_script,
    'redis': containers.redis.get_script,
    'sentry': containers.sentry.get_script,
    'solr': containers.solr.get_script,
    'uwsgi': containers.uwsgi.get_script,
}

def get_lxc_ip(name=None):
    # get lxc-ip script if doesn't exist
    out = run('test -e /usr/local/bin/lxc-ip', quiet=True,
        warn_only=True)
    if out.return_code != 0:
        with hide('stdout'):
            sudo('wget {0} -O /usr/local/bin/lxc-ip ; chmod +x /usr/local/bin/lxc-ip'.format(
                LXC_IP_LINK))
    with hide('stdout'):
        out = sudo('/usr/local/bin/lxc-ip -n {0}'.format(name))
    return out

@task
def create(name=None, distro='ubuntu-cloud', release='', arch='',
    user_data_file=None, base_containers=None, **kwargs):
    """
    Creates a new Container

    :param name: Name of container
    :param distro: Name of base distro (default: ubuntu-cloud)
    :param release: Name of base distro release
    :param arch: Architecture of container
    :param user_data_file: Path to user data file for cloud-init
        (ubuntu cloud images only)
    :param base_containers: Base Containers (ignores user_data_file)

    """
    if not name:
        raise StandardError('You must specify a name')
    cmd = 'lxc-create -n {0} -t {1}'.format(name, distro)
    if arch:
        cmd += ' -a {0}'.format(arch)
    # everything below is for template options
    cmd += ' --'
    if release:
        cmd += ' -r {0}'.format(release)
    tmp_file = None
    if distro == 'ubuntu-cloud' and user_data_file or base_containers:
        if base_containers:
            for c in base_containers:
                if c not in CONTAINERS.keys():
                    raise StandardError('Unknown base container: {0}'.format(c))
            print('Provisioning with base container(s): {0}'.format(
                ', '.join(base_containers)))
            user_data_file = tempfile.mktemp()
            with open(user_data_file, 'w') as f:
                for c in base_containers:
                    f.write(CONTAINERS[c]())
        else:
            if not os.path.exists(user_data_file):
                raise StandardError('User data file must exist')
            # create remote user data file for use with lxc-create
        tmp_file = os.path.join('/tmp',
            ''.join(random.sample(string.letters, 5)))
        put(user_data_file, tmp_file)
        # change ubuntu password since ubuntu-cloud has no password
        # therefore console doesn't work
        sudo(r"sed -i '2s/^/echo ubuntu:ubuntu | chpasswd \n/' {0}".format(tmp_file))
        cmd += ' -u {0}'.format(tmp_file)
    sudo(cmd)
    if tmp_file:
        sudo('rm -f {0}'.format(tmp_file))

@task
def clone(name=None, source=None, size=2, **kwargs):
    """
    Creates a new Container

    :param name: Name of new container
    :param source: Name of source container
    :param size: Size of new container (in GB, default: 2)

    """
    if not name or not source:
        raise StandardError('You must specify a name and source')
    sudo('lxc-clone -o {0} -n {1} -s {2}G'.format(source, name, size))

@task
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
    print('Creating archive...')
    with cd(os.path.join(LXC_PATH, name)), hide('stdout'):
        sudo('tar czf {0} .'.format(tmp_file))
    print('Downloading {0} ...'.format(export_name))
    get(tmp_file, export_name)
    sudo('rm -f {0}'.format(tmp_file))

@task
def import_container(name=None, local_path=None, **kwargs):
    """
    Imports a container from an export

    :param name: Name of container
    :param local_path: Path to exported container (tarball)

    """
    if not name or not os.path.exists(local_path):
        raise StandardError('You must specify a name and file must exist')
    tmp_file = '/tmp/{0}.tar.gz'.format(name)
    print('Uploading archive...')
    put(local_path, tmp_file)
    dest_path = os.path.join(LXC_PATH, name)
    sudo('mkdir -p {0}'.format(dest_path))
    print('Extracting...')
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
    print('Imported {0} successfully...'.format(name))

@task
def list(**args):
    """
    List all Containers

    """
    sudo('lxc-list')

@task
def start(name=None, ephemeral=False, **kwargs):
    """
    Starts a Container

    :param name: Name of container
    :param ephemeral: Disregard changes after stop (default: False)

    """
    if not name:
        raise StandardError('You must specify a name')
    cmd = 'lxc-start -n {0} -c /tmp/{0}.lxc.console'.format(name)
    if ephemeral:
        cmd = 'lxc-start-ephemeral -o {0}'.format(name)
    sudo('nohup {0} -d > /dev/null 2>&1'.format(cmd))

@task
def console(name=None, **kwargs):
    """
    Connects to Container console

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    open_shell('sudo lxc-console -e b -n {0} ; exit'.format(name))

@task
def stop(name=None, **kwargs):
    """
    Stops a Container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    sudo('lxc-stop -n {0}'.format(name))

@task
def destroy(name=None, **kwargs):
    """
    Destroys a Container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    sudo('lxc-destroy -n {0} -f'.format(name))

@task
def forward_port(name=None, port=None, **kwargs):
    """
    Forwards a host port to a container port

    :param name: Name of container
    :param port: Port on container

    """
    # find open port on host
    while True:
        dport = random.randint(10000, 50000)
        out = sudo('netstat -lnt | awk \'$6 == "LISTEN" && $4 ~ ".{0}"\''.format(
            dport))
        if out == '':
            break
    # get ip of container
    container_ip = get_lxc_ip(name)
    with hide('stdout'):
        sudo('iptables -t nat -A PREROUTING -p tcp --dport {0} ' \
            '-j DNAT --to-destination {1}:{2}'.format(dport, container_ip,
            port))
        sudo('iptables -t nat -A PREROUTING -p udp --dport {0} ' \
            '-j DNAT --to-destination {1}:{2}'.format(dport, container_ip,
            port))
        # save rules
        sudo('iptables-save > /etc/crate.iptables')
    print('Service available on host port {0}'.format(dport))

@task
def list_ports(name=None, **kwargs):
    """
    Removes a container port forward

    :param name: Name of container

    """
    # get ip of container
    container_ip = get_lxc_ip(name)
    # only show tcp to prevent duplicates for udp
    cur = sudo('iptables -L -t nat | grep {0} | grep tcp'.format(container_ip),
        warn_only=True, quiet=True)
    if cur:
        for l in cur.splitlines():
            if l:
                dport = cur.split()[-2].split(':')[1]
                target = cur.split()[-1].split(':')[-1]
                print('Port: {0} Target: {1}'.format(dport, target))
    else:
        print('No port forwards for {0}'.format(name))

@task
def remove_port(name=None, port=None, **kwargs):
    """
    Removes a container port forward

    :param name: Name of container
    :param port: Port on container

    """
    # get ip of container
    container_ip = get_lxc_ip(name)
    cur = sudo('iptables -L -t nat | grep {0}'.format(container_ip),
        warn_only=True, quiet=True)
    if cur:
        dport = cur.split()[-2].split(':')[1]
        sudo('iptables -t nat -D PREROUTING -p tcp --dport {0} ' \
            '-j DNAT --to-destination {1}:{2}'.format(dport, container_ip,
            port), warn_only=True, quiet=True)
        sudo('iptables -t nat -D PREROUTING -p udp --dport {0} ' \
            '-j DNAT --to-destination {1}:{2}'.format(dport, container_ip,
            port), warn_only=True, quiet=True)
        # save rules
        sudo('iptables-save > /etc/crate.iptables')
        print('Forward for port {0} removed'.format(port))

@task
def set_memory_limit(name=None, memory=256, **kwargs):
    """
    Sets memory limit for a Container

    :param name: Name of container
    :param memory: Max memory for container

    """
    if not name:
        raise StandardError('You must specify a name')
    mem = (int(memory) * 1048576) # convert from MB to Bytes
    print('Setting {0} memory limit to {1}MB'.format(name, memory))
    with hide('stdout'):
        sudo('lxc-cgroup -n {0} memory.limit_in_bytes {1}'.format(name, mem))

@task
def get_memory_limit(name=None, **kwargs):
    """
    Gets memory limit for a Container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    with hide('stdout'):
        out = sudo('lxc-cgroup -n {0} memory.limit_in_bytes'.format(name))
    mem = (int(out) / 1048576) # convert from bytes to MB
    if mem > 1048576 * 1048576:
        limit = 'Unlimited'
    else:
        limit = '{0}MB'.format(mem)
    print('Memory limit for {0}: {1}'.format(name, limit))

@task
def set_cpu_limit(name=None, percent=100, **kwargs):
    """
    Sets cpu limit for a Container

    :param name: Name of container
    :param percent: CPU priority in percent

    """
    if not name:
        raise StandardError('You must specify a name')
    print('Setting {0} CPU ratio to {1}%'.format(name, percent))
    # default cpu shares value is 1024
    ratio = int(1024 * (float(percent) / float(100)))
    with hide('stdout'):
        sudo('lxc-cgroup -n {0} cpu.shares {1}'.format(name, ratio))

@task
def get_cpu_limit(name=None, **kwargs):
    """
    Gets CPU limit for a Container

    :param name: Name of container

    """
    if not name:
        raise StandardError('You must specify a name')
    with hide('stdout'):
        out = sudo('lxc-cgroup -n {0} cpu.shares'.format(name))
    limit = int((float(int(out)) / float(1024)) * 100)  # convert to percent
    print('CPU limit for {0}: {1}%'.format(name, limit))
