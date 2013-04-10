# Base Containers
Crate provides a way to provision base boxes with pre-packaged functionality.
Such containers include Nginx, Redis, MongoDB, PostgreSQL, etc.  You can also
create your own.  See the `crate/containers` directory for samples.
Basically they are just shell scripts that are passed to the Ubuntu Cloud
image as a cloud-init script.  This also makes the Ubuntu Cloud image a
requirement.  Use the `-b` option when creating a container to specify
one or more base containers to be provisioned in your instance.  You can also
use `crate list-base-containers` to show the available bases.

