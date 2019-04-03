.. _monitoring:

Monitoring howto
================

Icinga2 follows an "apply logic style" for its configuration but it
does not disallow adding isolated services, to handle exceptions to
the rules.

Most of the service definitions are based on predefined
commands which are documented
`here <https://www.icinga.com/docs/icinga2/latest/doc/10-icinga-template-library/#plugin-check-commands-for-monitoring-plugins>`__.

Monitoring deployment
---------------------

Monitoring is deployed by importing the
`molecule/icinga/icinga-playbook.yml` playbook. The Icinga2 master is
`icinga-host`. See also
`inventories/common/host_vars/icinga-host/monitoring.yml` for specific
deployment attributes: icingaweb credentials, https, virtualhost fqdn.

Each host is monitored by default.

To disable monitoring for some host, you have to define a host variable
``not_monitored``.

Base system monitoring
^^^^^^^^^^^^^^^^^^^^^^

For each host we:

-  check ping (default host check in Icinga)
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
^^^^^^^^^^^^^^^^^^^^

A host can declare a git repo to be checked (designed originally for
`etckeeper`):

::

      vars.repos["Bling"] = {
        dir = "/var/git/bling"
      }

The git check command is sudoed.

Example of use in a role: `molecule/icinga/roles/deploy_dummy_monitoring_objects/tasks/main.yml`.

Disk and partitions monitoring
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^

A host can declare any process presence to be checked:

::

      vars.process["Incron"] = {
        procs_command = "incrond"
        procs_critical = "1:1"
      }

Example of use in a role: `molecule/icinga/roles/deploy_dummy_monitoring_objects/tasks/main.yml`.

Mail sending monitoring
^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^

A host can declare hosting web at a given fqdn:

::

      vars.http_vhosts["Secure Drop Forum"] = {
        http_vhost = "forum.enough.community"
        http_uri = "/c/devops"
        http_ssl = true
        http_string = "devops discussions"
      }

-  Each fqdn is processed via ``check_http`` from Icinga master and
   should provide ``http_string`` in answer's body.
-  Each fqdn is processed via ``check_http`` from Icinga master and
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

Example of use in a role: `molecule/weblate/roles/weblate/tasks/monitoring.yml`.

Since monitoring `http vhosts` happens often in  `enough.community`, an Ansible
role helps to declare it:

::

    - role: monitor_http_vhost
      http_vhost_name: Secure Drop Forum
      http_vhost_fqdn: "forum.{{ domain }}"
      http_vhost_uri: /c/devops
      http_vhost_string: "devops discussions"
      http_vhost_https: true

Torified Web services monitoring
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Similarly to `http_vhosts`, a host can declare a `tor_http_vhosts` dictionnary.
The main difference is that it is not a `fqdn` which is transmitted, but the
path of the service hostname. An Ansible role helps to declare it:

::

    - role: monitor_tor_http_vhost
      tor_hostname_file: /var/lib/tor/services/cloud/hostname
      tor_http_vhost_name: Cloud
      tor_http_vhost_uri: "/login"
      tor_http_vhost_string: "Forgot password"

.. note:: For now the only handled case concerns plain http over tor. TLS hasn't yet been defined.

DNS service monitoring
^^^^^^^^^^^^^^^^^^^^^^

A host can declare hosted zones files which can be checked via
``named-checkzone`` (syntax consistency) and ``check_whois`` (domain
expiration):

::

      /* Define zones and files for checks */
      vars.zones["Secure Drop Club"] = {
        fqdn = "enough.community"
        file = "/etc/bind/zones/masters/enough.community"
        view = "external"
      }

Example of use in a role: `molecule/bind/roles/monitoring-bind/tasks/main.yml`.

Maybe we could add a check dig on the A and NS records, and eventually
use ``zonemaster`` or a webservice providing ``zonemaster`` results.

Monitoring tweaking
-------------------

Service templates
^^^^^^^^^^^^^^^^^

A host can set a prefered service template, using the icinga variable
``vars.service_template``.

The templates can be found in `molecule/icinga/roles/icinga2/files/templates.conf`.

Hosts vars
^^^^^^^^^^

A host can define a list of lines to be added to its icinga configuration,
using the Ansible variable ``monitoring_host_vars``. Se e.g.
``inventories/common/host_vars/icinga-host/monitoring.yml`` for an example.

Default is empty.
