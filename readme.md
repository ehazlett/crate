# Crate
Linux container management.  Crate uses [Fabric](http://fabfile.org) to manage
remote hosts.  Currently tested on Ubuntu 12.04.  Similar to http://getdocker.io
but written in Python and intended for remote hosts.

# Setup
Using a virtualenv is preferred.

* `pip install -r requirements.txt`

# Operations
All operations are intended for remote hosts.  The remote host must also have
Linux Container (lxc) support.  For Ubuntu (only 12.04 tested) this is as easy
as `apt-get install lxc`.

Crate will help in creating, destroying, exporting, port forwarding, etc. Linux
containers.

To see a list of operations run `fab -l`.  For detailed usage use `-d`.  For example,
`fab -d create`.

# Vagrant
A [Vagrant](http://vagrantup.com) config is also provided for development
and testing.  Simply `vagrant up` to get a working environment.

# Examples
Since crate uses fabric, you simply use the `fab` command with host, etc.  For
the local vagrant VM, after provisioning you should see something like:

```
Your vagrant box should be available at 10.10.10.130

```

You can use the Vagrant IP as the remote host.  We will use the IP `10.10.10.130`
for the examples below.

Note: I create an alias for testing to avoid typing the `fab -H 10.10.10.130...`
every time.  I will leave it in the examples for clarity.

## Create Container

```
fab -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key create:testing,ubuntu,precise,amd64

debootstrap is /usr/sbin/debootstrap
Checking cache download in /var/cache/lxc/precise/rootfs-amd64 ...
Copy /var/cache/lxc/precise/rootfs-amd64 to /var/lib/lxc/testing/rootfs ...
Copying rootfs to /var/lib/lxc/testing/rootfs ...

##
# The default user is 'ubuntu' with password 'ubuntu'!
# # Use the 'sudo' command to run tasks as root in the container.
# ##
#
# 'ubuntu' template installed
# 'testing' created

```

Note: the first time this runs it will take a while as it has to download
packages.  After the first time it will be much faster as it will pull from cache.

## List Containers

```
fab -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key list

RUNNING

FROZEN

STOPPED
  testing

```

## Clone Container

```
fab -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key clone:testing,testing2

Tweaking configuration
Copying rootfs...
Updating rootfs...
'testing2' created
```

## Start Container

```
fab -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key start:testing
```

## Access Console

```
fab -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key console:testing
Type <Ctrl+b q> to exit the console

Ubuntu 12.04.2 LTS testing tty1

testing login:

```

Note: to disconnect, press `Ctrl+b, q`

## Port Forward
This will select a random available port on the host and setup forwarding to the
container port.

```
fab -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key forward_port:testing,80

Service available on host port 27802
```

You can now access the container application via the host high port, i.e. 10.10.10.130:27802

## List Ports

```
fab -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key list_ports:testing

Port: 27802 Target: 80

```

## Remove Port Forward

```
fab -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key remove_port:testing,80

Port forward for 80 removed
```

## Stop Container

```
fab -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key stop:testing
```

## Export Container

```
fab -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key export_container:testing

Creating archive...
Downloading testing-2013-03-30.tar.gz ...
```

## Destroy Container

```
fab -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key destroy:testing
```

## Import Container

```
fab -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key import_container:testing,testing-2013-03-30.tar.gz

Uploading archive...
Extracting...
Imported testing successfully...
```

