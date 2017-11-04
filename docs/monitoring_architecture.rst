Monitoring architecture
=======================

Icinga2 overview
----------------

Icinga 2 is very flexible and doesn't impose monitoring
architecture. So we have to define it. The simplest is to follow the
`master with clients
setup <https://www.icinga.com/docs/icinga2/latest/doc/06-distributed-monitoring/#master-with-clients>`__,
which looks like the good old Nagios/NRPE. It implies:

-  Getting a master server (including web GUI),
-  Getting a client for each VM on which you would execute checks.

This is flexible because Icinga use basically the same software for clients
and masters. It's their configuration which define them as master or client.
This has the benefits that configuration objects may be pushed from
master to clients, so you can absolutely forget the ugly "NRPE commands"
files.

Our master server deployment is defined in `molecule/icinga/roles/icinga2`.

Our client deployment is defined in `molecule/icinga/roles/icinga2_client`.

By the way, executables checks are still managed locally on each computer, as
well as required sudo perms. To deploy it, a common role is defined in
`molecule/icinga/roles/icinga2_common`.

Last but not least, Icinga2 define "zones", which is a way to control
information sharing over the monitoring infrastructure. Usually we
define (for a master/clients setup):

-  a global zone for shared configuration among all the cluster;
-  a master zone for the master;
-  a client zone for each client which get the master zone as parent
   zone.

This way, each client doesn't know about others (the master will
distribute only needed stuffs).

Molecule test environment
-------------------------

In `molecule/icinga`, we define a test environment with a master and a client.

Now we have a correct set up for Icinga master and clients, NginX, Icingaweb2
and Let's Encrypt. Some tests are checking that the playbook is well executed.

Object logic style vs Apply logic style
---------------------------------------

Let's speak about the Icinga configuration philosophy. In what
follows, "service" means "check" (it's Nagios/Icinga nomenclature).

Most deployments I seen are clearly inspired from a "Nagios" pattern.
It is what we can call the "Object logic style".
By doing this, you roughly define manually one service for each check you will
enable.

Adding a new check means copy/pasting a service, which is not terribly
aesthetic (think about how does looks like the configuration for one hundred of http
vhosts). Moreover it is not very clever: think about monitoring a http host.
Maybe you would like to monitor (at least) an answer on :80, another on :443,
and also the validity of the certificate. Doing this Nagios in the Nagios way
means that you will copy/paste 3 times the same-but-not-exactly service (again,
think about how does looks like the configuration for one hundred vhosts). And by doing
this, each extra check will bloat your configuration.

Automation could help us to manage this kind of stuff. But I would not be
so proud to do so. :)

Icinga2 offer a much more flexible and clever way to instantiate our
checks, in a way much more descriptive; thus more concise, more
aesthetic, more clever and terribly lovely. This is the "`apply logic
style <https://www.icinga.com/docs/icinga2/latest/doc/08-advanced-topics/#advanced-use-of-apply-rules>`__".
You can describe every kind of behavior, the way you want, using a
quite complete language (including list and associative array), as an
host attribute.

So directly at host level you can add any attribute you like, e.g. a
list of hardware block devices, a list of mounted volumes, a list of
vhosts and some associated useful attributes, a list of process you
would like to check and their associated limits, a list of git repos to
be checked, etc.

Those attributes provided, you can define any generic service you like
which will take into account these attributes, the best way possible.
Since it it generic code, you don't have any need to template this part
of code. To give an idea of the simplicity of the Icinga2 language, here
follows how you generically check all the certificates of all the vhosts
which are declared using TLS:

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

with an host which simply contains this kind of declaration:

::

      vars.http_vhosts[""Forum""] = {
        http_vhost = ""forum.securedrop.club""
        http_ssl = true
      }

Well, fortunately the description may add a list of some attended
strings at some given URI, and any other parameter of your choice,
provided that you write the code which will exploit it.

The main monitoring configuration for securedrop.club is available in
`molecule/icinga/roles/icinga2/files/services/` and deployed in the
global Icinga zone, thus available to all the cluster.

By doing so, with a very concise configuration at host level, and a little bit
of easy generic code, we were able to check for vhosts, DNS zones consistency,
DNS views consistency, attended processes, attended vhosts, attended output
IPs, git repos, mails queues, services banners (ssh, smtp, etc.), upgrades,
running kernels, mailname consistency, volumes, databases, etc.
