# Base Container: PostgreSQL
This provides a default [PostgreSQL](http://www.postgresql.org/) setup.  This module is managed with Puppet.

This container also includes pgbouncer.  The default configuration only allows
local access to port 5432 and exposes pgbouncer on port 6432.

# Configuration
Ports:
* 6432 (pgbouncer)

# Misc.
Puppet Module Source: https://github.com/arcus-io/puppet/tree/master/modules/postgresql

