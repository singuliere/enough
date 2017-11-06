Ansible
=======

Running
-------

The `ansible repository
<http://lab.securedrop.club/main/securedrop-club/>`_ is run from the
`/srv/checkout` directory of the `ansible.securedrop.club` virtual
machine as follows:

.. code::

   ansible-playbook --private-key infrastructure_key \
                    --user debian \
                    -i inventory \
                    securedrop-club-playbook.yml

Inventory
---------

The ansible inventory is created by the
``molecule/infrastructure/create.yml`` playbook and stored in the
``hosts.yml`` file every time the ``molecule create`` command runs.
The inventory is read from the ``hosts-base.yml`` file, the IP address of each
host is added and the result is written into ``hosts.yml``.

Updating
--------

The `/srv/checkout` directory is a clone of the `ansible repository
<http://lab.securedrop.club/main/securedrop-club/>`_ and can be updated with:

.. code::

   git fetch ; git rebase

Testing a production upgrade
----------------------------

Testing strategy to verify we can go from nothing to the most recent
version and also upgrade from the currently used version to the most
recent version. Assuming we always tag the repository before applying
it to the production.

Using an empty tenant:

* git checkout previous-version-tag
* molecule verify # nothing -> previous-version-tag
* git checkout master # version under test
* molecule verify # previous-version-tag -> master
* molecule tests # nothing -> master
