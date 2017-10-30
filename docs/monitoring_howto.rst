Monitoring howto
================

As explained in "Object logic style vs Apply logic style" we
follow an "apply logic style" for icinga 2 configuration, with is
pretty well suited for generic monitoring setup on homogenous clusters.
Fortunately it does not disallow adding isolated services (à la Nagios),
so future exceptions to the rules may be handled this way.

For most of the service definitions, they are based on predefined
commands which are documented
`here <https://www.icinga.com/docs/icinga2/latest/doc/10-icinga-template-library/#plugin-check-commands-for-monitoring-plugins>`__.

Monitoring deployment
---------------------

Monitoring is deployed as long as the playbook
``molecule/icinga/icinga-playbook.yml`` has been imported. The Icinga2 master
is defined by the variable ``monitoring_master`` and set to ``icinga-host`` in
``group_vars/all/infrastructure.yml``. See also
``host_vars/icinga-host/monitoring.yml`` for specific monitoring attributes.

Each host is monitored by default.

To disable monitoring for some host, you have to define a host variable
``not_monitored``.

Base system monitoring
----------------------

For each host we: 

-  check ping (default host check in icinga) 
-  check ssh 
-  check apt 
-  check etckeeper
-  check icinga 
-  check load 
-  check procs 
-  check swap when ``vars.swap`` is defined 
-  check users 
-  check run\_kernel (check if it run the most up-to-date kernel) 
-  check fail2ban process
-  check sshd process 
-  check rsyslogd process 
-  check icinga2 process
-  check cron process

Git repos monitoring
--------------------

A host can declare a git repo to be checked (designed originally for
``etckeeper``):

::

      vars.repos["Bling"] = {
        dir = "/var/git/bling"
      }

The git check command is sudoed.

Example of use in a role: ``molecule/icinga/roles/deploy_dummy_monitoring_objects/tasks/main.yml``.

Disk and partitions monitoring
------------------------------

A host can declare any partition to be checked:

::

      vars.disks["disk"] = {
      }
      vars.disks["disk /"] = {
        disk_partitions = "/"
      }
      vars.disks["disk /var"] = {
        disk_partitions = "/var"
      }
      vars.disks["disk /tmp"] = {
        disk_partitions = "/tmp"
      }

Processes monitoring
--------------------

A host can declare any process presence to be checked:

::

      vars.process["Incron"] = {
        procs_command = "incrond"
        procs_critical = "1:1"
      }

Example of use in a role: ``molecule/icinga/roles/deploy_dummy_monitoring_objects/tasks/main.yml``.

Mail sending monitoring
-----------------------

A host can declare any non-null value in ``vars.sendmail``. Then
mailname, mail queue and process are checked.

It's currently not sufficient.

I wrote some time ago a qshape based test which is suitable to detect
delivery problems for mass mailling (much better than the mail queue
which can legitimately grows when needed). But it is not adapted for
sparse emailling.

So, some nice projects would be of interest to monitor our ability to
send emails:

-  check qshape.
-  check rbls.
-  a mail loop test (verify the self-delivery of a sent mail gone via
   another relay)
-  a mail delivery test (verify the delivery of a sent mail in some of
   the majors mails domains)

Web services monitoring
-----------------------

A host can declare hosting web at a given fqdn:

::

      vars.http_vhosts["Secure Drop Forum"] = {
        http_vhost = "forum.securedrop.club"
        http_uri = "/c/devops"
        http_ssl = true
        http_string = "devops discussions"
      }

-  Each fqdn is processed via ``check_http`` from icinga master and
   should provide ``http_string`` in answer's body.
-  Each fqdn is processed via ``check_http`` from icinga master and
   should *not* provide some strings in the answer. It is useful to
   prevent from accidentally deploy spywares. For now, spywares checked
   are:

   -  googleapis.com
   -  cloudflare.com
   -  google-analytics.com
   -  gravatar.com

-  If ``http_ssl = true`` the check is processes using https and the TLS
   certificate is retrieved for validity check.

Moreover if a host declare ``vars.httpd = "apache"`` or
``vars.httpd = "apache2"`` or ``vars.httpd = "nginx"``, then processes
check are executed.

If a host declare ``vars.sqlserver = "mysql"`` or
``vars.sqlserver = "mariadb"`` or ``vars.sqlserver = "pgsql"``, then
processes check are executed.

It is probably easily feasible to associate a list of scripts to each
fqdn for more advanced checks (check result of a POST, etc.) if needed.

Example of use in a role: ``molecule/weblate/roles/weblate/tasks/monitoring.yml``.

DNS service monitoring
----------------------

A host can declare hosted zones files which can be checked via
``named-checkzone`` (syntax consistency) and ``check_whois`` (domain
expiration):

::

      /* Define zones and files for checks */
      vars.zones["Secure Drop Club"] = {
        fqdn = "securedrop.club"
        file = "/etc/bind/zones/masters/securedrop.club"
        view = "external"
      }

Example of use in a role: ``molecule/bind/roles/monitoring-bind/tasks/main.yml``.

Maybe we could add a check dig on the A and NS records, and eventually
use ``zonemaster`` or a webservice providing ``zonemaster`` results.
