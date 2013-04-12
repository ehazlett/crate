# Crate
Linux container management.  Crate uses [Fabric](http://cratefile.org) to manage
remote hosts.  Currently tested on Ubuntu 12.04.  Similar to the spectacular http://docker.io
but written in Python and intended for remote hosts.

Crate is designed to be a wrapper around Linux containers and use the already existing lxc-tools.  For example, crate will use the existing methods for building images.  There are no "pre-built" images to download.  This is done for security purposes -- you build the containers you want.

# Setup
Using a virtualenv is preferred.

Crate is still in development so install directly from Github:

`pip install https://github.com/ehazlett/crate/archive/master.zip`

# Operations
All operations are intended for remote hosts.  The remote host must also have
Linux Container (lxc) support.  For Ubuntu (only 12.04 tested) this is as easy
as `apt-get install lxc`.

Crate will help in creating, destroying, exporting, port forwarding, etc. Linux
containers.

To see a list of operations run `crate -h`

# Vagrant
A [Vagrant](http://vagrantup.com) config is also provided for development
and testing.  Simply `vagrant up` to get a working environment.

# More Info
For detailed documentation on topics such as advanced usage, base containers, etc.
see [here](https://github.com/ehazlett/crate/tree/master/docs/).
