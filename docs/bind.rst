DNS
===

Registrar
---------

The `securedrop.club` domain name is registered at `Gandi
<https://gandi.net>`_ under the user SD11514-GANDI.

Mail
----

The `contact mail <contact@securedrop.club>`_ is a forwarding alias
hosted at Gandi and is used as the primary contact for all
`securedrop.club` resources (hosting etc.). In case a password is lost
this is the mail receiving the link to reset the password etc.

Zones
-----

securedrop.club
```````````````

The `securedrop.club` zone is managed on a dedicated virtual machine
`ns1.securedrop.club`. It is generated via `the bind playbook
<http://lab.securedrop.club/main/securedrop-club/blob/master/molecule/bind/bind-playbook.yml>`_.


* The port udp/53 is open to all but recursion is only allowed for IPs
  of the securedrop-club VMs
* An **A** record is created for all existing VM names
* A **CNAME** record is created for all VM names without the `-host` suffix
* Manually maintained records are added to `the bind playbook <http://lab.securedrop.club/main/securedrop-club/blob/master/molecule/bind/bind-playbook.yml>`_.
* The `SPF` **TXT** record help :doc:`send mail <postfix>` successfully.

test.securedrop.club
````````````````````

The `test.securedrop.club` zone is managed on the same dedicated virtual machine
`ns1.securedrop.club`. It is generated via `the bind playbook
<http://lab.securedrop.club/main/securedrop-club/blob/master/molecule/bind/bind-playbook.yml>`_.

It can be updated locally by the `debian` user via ``nsupdate``. This allow
any securedrop.club's administrator to setup new preproduction testing
subdomains. Exemple:

::

  \ SD / debian@bind-host:~$ nsupdate <<EOF
  server localhost
  zone test.securedrop.club
  update add bling.test.securedrop.club. 1800 TXT "Updated by nsupdate"
  show
  send
  quit
  EOF

VMs resolvers
-------------

Each VM is set to use `ns1.securedrop.club` as a resolver via `the bind-client playbook <http://lab.securedrop.club/main/securedrop-club/blob/master/molecule/bind/bind-client-playbook.yml>`_
which also sets the FQDN.
