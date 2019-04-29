.. _bind:

DNS
===

Registrar
---------

The `enough.community` domain name is registered at `Gandi
<https://gandi.net>`_ under the user EC8591-GANDI.

After the `bind-host` virtual machine is created, click on `Glue record management` in the Gandi web
interface and set ns1 to the IP, i.e. 51.68.79.8 and wait a few
minutes. Click on `Update DNS` and set the `DNS1` server to
ns1.enough.community and click on `Add Gandi's secondary nameserver`
which should add a new entry in DNS2: it will automatically act as a
secondary DNS.

The `bind-host` virtual machine should be initialized before any other
because everything depends on it.

.. code::

   ansible-playbook -l bind-host \
                    --private-key infrastructure_key \
                    -i inventories/common \
                    enough-community-playbook.yml 

Mail
----

The `admin mail <admin@enough.community>`_ is
hosted at Gandi and is used as the primary contact for all
`enough.community` resources (hosting etc.). In case a password is lost
this is the mail receiving the link to reset the password etc.

Zones
-----

enough.community
````````````````

The `enough.community` zone is managed on a dedicated virtual machine
`ns1.enough.community`. It is generated via `the bind playbook
<http://lab.enough.community/main/enough-community/blob/master/molecule/bind/bind-playbook.yml>`_.


* The port udp/53 is open to all but recursion is only allowed for IPs
  of the enough-community VMs
* An **A** record is created for all existing VM names
* A **CNAME** record is created for all VM names without the `-host` suffix
* Manually maintained records are added to `the bind playbook <http://lab.enough.community/main/enough-community/blob/master/molecule/bind/bind-playbook.yml>`_.
* The `SPF` **TXT** record help :doc:`send mail <postfix>` successfully.

test.enough.community
`````````````````````

The `test.enough.community` zone is managed on the same dedicated virtual machine
`ns1.enough.community`. It is generated via `the bind playbook
<http://lab.enough.community/main/enough-community/blob/master/molecule/bind/bind-playbook.yml>`_.

It can be updated locally by the `debian` user via ``nsupdate``. This enables
any enough.community's administrator to setup new preproduction testing
subdomains. Exemple:

::

  - E - debian@bind-host:~$ nsupdate <<EOF
  server localhost
  zone test.enough.community
  update add bling.test.enough.community. 1800 TXT "Updated by nsupdate"
  show
  send
  quit
  EOF

VMs resolvers
-------------

Each VM is set to use `ns1.enough.community` as a resolver via `the bind-client playbook <http://lab.enough.community/main/enough-community/blob/master/molecule/bind/bind-client-playbook.yml>`_
which also sets the FQDN.
