Monitoring architecture
=======================

Icinga2 overview
----------------

Icinga2 is very flexible and doesn't impose monitoring
architecture. So we have to define it. The simplest is to follow the
`master with clients
setup <https://www.icinga.com/docs/icinga2/latest/doc/06-distributed-monitoring/#master-with-clients>`__. It implies:

- getting a master server (including web GUI),
- getting a client for each VM on which you would execute checks.

Icinga2 uses the same software for clients and masters and their
configuration defines if one is master or client. We can use the same
configuration objects for master and clients.

Our master server deployment is defined in `molecule/icinga/roles/icinga2`.

Our client deployment is defined in `molecule/icinga/roles/icinga2_client`.

Executables checks are managed locally on each computer, as
well as required sudo permissions. To deploy them, a common role is defined in
`molecule/icinga/roles/icinga2_common`.

Icinga2 define "zones", which is a way to control information sharing
over the monitoring infrastructure. We define:

- a global zone for the configuration shared among all the cluster;
- a master zone for the master;
- a client zone for each client which the master zone as a parent.

Client dont't know about each other (the master will distribute only
what is required).

Molecule test environment
-------------------------

In `molecule/icinga`, we define a test environment with a master and a client.

A set up for Icinga2 needs master and clients, NginX, Icingaweb2
and Let's Encrypt. Tests are checking that the playbook is well executed.

Apply logic style
-----------------

Icinga2 uses the "`apply logic style
<https://www.icinga.com/docs/icinga2/latest/doc/08-advanced-topics/#advanced-use-of-apply-rules>`__".
All behavior is described using a language (including list and
associative array), as an host attribute (e.g. a list of hardware
block devices, a list of mounted volumes, a list of vhosts and some
associated attributes, a list of process you would like to
check and their associated limits, a list of git repos to be checked,
etc.)

Based on those attributes provided, generic service can be defined.
Here is how one can check all the certificates of all the vhosts which
are declared to use TLS:

::

    apply Service ""Check TLS certificate "" for (http_vhost => config in host.vars.http_vhosts) {
        import ""generic-service""

        check_command = ""http""
        vars.http_address = config.http_vhost
        command_endpoint = "" ... ""
        vars.http_certificate = 21
        vars.http_sni = true

        vars += config
        assign where config.http_ssl == true
    }

with n host which contains this declaration:

::

      vars.http_vhosts[""Forum""] = {
        http_vhost = ""forum.enough.community""
        http_ssl = true
      }

The main monitoring configuration for enough.community is available in
`molecule/icinga/roles/icinga2/files/services/` and deployed in the
global Icinga zone, thus available to all the cluster.

There are checks for vhosts, DNS zones consistency, DNS views
consistency, attended processes, attended vhosts, attended output IPs,
git repos, mails queues, services banners (ssh, smtp, etc.), upgrades,
running kernels, mailname consistency, volumes, databases, etc.
