# Base Containers
Crate provides a way to provision base boxes with pre-packaged functionality.
Such containers include Nginx, Redis, MongoDB, PostgreSQL, etc.  You can also
create your own.  See the `crate/containers` directory for samples.
Basically they are just shell scripts that are passed to the Ubuntu Cloud
image as a cloud-init script.  This also makes the Ubuntu Cloud image a
requirement.  Use the `-b` option when creating a container to specify
one or more base containers to be provisioned in your instance.  You can also
use `crate list-base-containers` to show the available bases.

# Builtin Containers

* [Apache2](./apache2.md)
* [Core](./core.md)
* [Graphite](./graphite.md)
* [Graylog2](./graylog2.md)
* [HAProxy](./haproxy.md)
* [Memcached](./memcached.md)
* [MongoDB](./mongodb.md)
* [MySQL](./mysql.md)
* [Nginx](./nginx.md)
* [OpenResty](./openresty.md)
* [Postgres](./postgres.md)
* [Puppet Dashboard](./puppetdashboard.md)
* [Puppet DB](./puppetdb.md)
* [Puppet Master](./puppetmaster.md)
* [RabbitMQ](./rabbitmq.md)
* [Redis](./redis.md)
* [Sensu](./sensu.md)

