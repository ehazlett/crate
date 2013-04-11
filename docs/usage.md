# Crate Usage
The following examples assume you are working with the Crate vagrant VM.

For testing, after building the local vagrant VM you should see something like:

```
Your vagrant box should be available at 10.10.10.130
```

You can use the Vagrant IP as the remote host.  We will use the IP `10.10.10.130`
for the examples below.

Note: I create an alias for testing to avoid typing the `crate -H 10.10.10.130...`
every time.  I will leave it in the examples for clarity.

## Create Container
This will create a default Ubuntu container.  You will need to either specify
a password `--password` or SSH public key `-s` to login to the Ubuntu containers.

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key create --name testing --distro precise --password ubuntu

debootstrap is /usr/sbin/debootstrap
Checking cache download in /var/cache/lxc/precise/rootfs-amd64 ...
installing packages: vim,ssh
Downloading ubuntu precise minimal ...
I: Retrieving Release
I: Retrieving Release.gpg
I: Checking Release signature
I: Valid Release signature (key id 630239CC130E1A7FD81A27B140976EAF437D05B5)
I: Retrieving Packages
I: Validating Packages
I: Retrieving Packages
I: Validating Packages
I: Resolving dependencies of required packages...
I: Resolving dependencies of base packages...

...

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

## Create Container (fedora)
This will create a default Fedora container.

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key create --name testing-fedora --distro fedora --password ubuntu

...

Download complete.
Copy /var/cache/lxc/fedora/x86_64/14/rootfs to /var/lib/lxc/base-fedora/rootfs ...
Copying rootfs to /var/lib/lxc/base-fedora/rootfs ...setting root passwd to root
installing fedora-release package
container rootfs and config created
'fedora' template installed
'base-fedora' created
```

## Create Container from base containers

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key create --name testing -b nginx,uwsgi --password ubuntu
```

## Create Container and provision with custom user data script (shell)

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key create --name testing --password ubuntu -f /path/to/script.sh
```

or via remote script:

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key create --name testing --password ubuntu -f http://gist.github.com/user/gistfile.sh
```

## List Containers

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key list

RUNNING

FROZEN

STOPPED
  testing

```

## Clone Container

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key clone --name testing2 --source testing

Tweaking configuration
Copying rootfs...
Updating rootfs...
'testing2' created
```

## Start Container

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key start --name testing
```

## Start Container (ephemeral)

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key start --name testing --ephemeral
```

## Access Console

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key console --name testing
Type <Ctrl+b q> to exit the console

Ubuntu 12.04.2 LTS testing tty1

testing login:

```

This is the console for Fedora:

```
Type <Ctrl+b q> to exit the console

Fedora release 14 (Laughlin)
Kernel 3.2.0-38-virtual on an x86_64 (tty1)

base-fedora login:
```

Note: to disconnect, press `Ctrl+b, q`

## Container CPU Limits

Get current limit (in percent):

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key get-cpu-limit -n testing

CPU limit for testing: 100%
```

Set new limit (in percent):
```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key set-cpu-limit -n testing -p 50

Setting testing CPU ratio to 50%
```

## Container Memory Limits

Get current limit (in MB):

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key get-memory-limit -n testing

Memory limit for testing: Unlimited
```

Set new limit (in MB):
```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key set-memory-limit -n testing -m 128

Setting testing memory limit to 128MB
```

## Port Forward
This will select a random available port on the host and setup forwarding to the
container port.

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key forward-port --name testing --port 80

Service available on host port 27802
```

You can now access the container application via the host high port, i.e. `10.10.10.130:27802`

## List Ports

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key list-ports --name testing

Port: 27802 Target: 80

```

## Remove Port Forward

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key remove-port --name testing --port 80

Port forward for 80 removed
```

## Stop Container

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key stop --name testing
```

## Export Container

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key export --name testing

Creating archive...
Downloading testing-2013-03-30.tar.gz ...
```

## Destroy Container

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key destroy --name testing
```

## Import Container

```
crate -H 10.10.10.130 -u vagrant -i ~/.vagrant.d/insecure_private_key import --name testing --local-path testing-2013-03-30.tar.gz

Uploading archive...
Extracting...
Imported testing successfully...
```
