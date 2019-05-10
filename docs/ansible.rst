Ansible
=======

Secrets
-------

The default credentials (for Weblate, Discourse etc.) are only
suitable for integration testing and must be overriden before
deploying on publicly available hosts. The recommended way of doing this is to:

* create a repository in `~/.enough/enough.community/inventory`
* for each files containing secrets i.e. {host,group}_vars/\*\*/\*.yml`) create a matching file in
  `~/.enough/enough.community/inventory`
* encrypt those files with `ansible vault <https://docs.ansible.com/ansible/latest/user_guide/vault.html>`_
* share the password to decrypt the files with trusted administrators
* push in a private repository

The encrypted secrets are kept in a private repository to not be
publicly exposed to brute force attacks.

Creation
--------

Manually create `~/.enough/enough.community/inventory/group_vars/all/clouds.yml`
by copying `clouds.yml.example` and getting values from `~/openrc.sh`
and check it works:

.. code::

   $ export OS_CLIENT_CONFIG_FILE=~/.enough/enough.community/group_vars/all/clouds.yml
   $ openstack --os-cloud ovh server list

.. code::

   $ echo domain: enough.community | sudo tee ~/.enough/enough.community/group_vars/all/domain.yml

Getting the production repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code::

   $ git clone git@lab.enough.community:production/enough.git ~/.enough/enough.community
   $ ansible-vault decrypt \
                   --vault-password-file ~/.enough/enough.community/vault_pass.txt \
                   ~/.enough/enough.community/infrastructure_key

Running
-------

Creating new hosts
~~~~~~~~~~~~~~~~~~

.. note:: do not run the following from a git checkout. If run from
          sources, the test environment will be used instead of the
	  production environment.

.. code::

   $ python -m enough.internal.cmd --domain enough.community host create some-host
   $ python -m enough.internal.cmd --domain enough.community host inventory

It will set the IP address of the new host into `~/.enough/enough.community/hosts.yml`.

.. code::

  all:
    hosts:
      bind-host: {ansible_host: 51.68.89.70}
      wereport-host: {ansible_host: 51.68.88.149}


Updating
~~~~~~~~

The `ansible repository
<http://lab.enough.community/main/infrastructure/>`_ is run as follows:

.. code::

   $ export MOLECULE_FILE=$(pwd)/molecule/preprod/molecule.yml
   $ ansible-playbook --private-key ~/.enough/enough.community/infrastructure_key \
                      --vault-password-file=~/.enough/enough.community/vault_pass.txt \
                      -i inventories/common \
                      -i ~/.enough/enough.community/inventory \
                      enough-community-playbook.yml

Some hosts contain private information that belong to users who only
trust some administrators of the infrastructure. These hosts only have
the ssh public keys of the trusted administrators and are listed in a
dedicated inventory subdirectory.  For instance, the administrator
`dachary` owns the the inventory directory `inventories/dachary`. This
administrator can then run the playbook on all the common
infrastructure as well as all the hosts that can only be accessed by
them as follows:

.. code::

   ansible-playbook --private-key ~/.enough/enough.community/infrastructure_key \
                    --vault-password-file=~/.enough/enough.community/vault_pass.txt \
                    -i inventories/common \
                    -i inventories/dachary \
                    -i ~/.enough/enough.community/inventory \
                    enough-community-playbook.yml
