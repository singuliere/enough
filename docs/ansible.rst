Ansible
=======

Secrets
-------

The default credentials (for Weblate, Discourse etc.) are only
suitable for integration testing and must be overriden before
deploying on publicly available hosts. The recommended way of doing this is to:

* create a repository in `~/.enough/enough.community`
* for each files containing secrets in `inventories/common`
  (i.e. {host,group}_vars/\*\*/\*.yml`) create a matching file in
  `~/.enough/enough.community`
* encrypt those files with `ansible vault <https://docs.ansible.com/ansible/latest/user_guide/vault.html>`_
* share the password to decrypt the files with trusted administrators
* push in a private repository

The encrypted secrets are kept in a private repository to not be
publicly exposed to brute force attacks.

Creation
--------

Manually create `~/.enough/enough.community/group_vars/all/clouds.yml` from `~/openrc.sh` and check it works:

.. code::

   $ OS_CLIENT_CONFIG_FILE=~/.enough/enough.community/group_vars/all/clouds.yml openstack --os-cloud ovh server list

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

From a checkout of the `infrastructure
<https://lab.enough.community/main/infrastructure>`_ repository:

.. code::

   $ export MOLECULE_FILE=$(pwd)/molecule/preprod/molecule.yml
   $ ansible-playbook --private-key ~/.enough/enough.community/infrastructure_key \
                    --vault-password-file=~/.enough/enough.community/vault_pass.txt \
                    -i inventories/common \
                    -i ~/.enough/enough.community \
                    molecule/infrastructure/create.yml

It will create the `inventories/01-hosts.yml` file, which must be
manually copied to `~/.enough/enough.community/01-hosts.yml` and committed to
the repository.

.. note::

   The ansible-playbook run will fail with ``no filter named
   'molecule_header'`` but it is ok to ignore that error.

.. code::

    all:
      hosts:
        new-host:
          ansible_host: 51.68.78.253
          ansible_port: '22'
          ansible_user: debian


Updating
~~~~~~~~

The `ansible repository
<http://lab.enough.community/main/infrastructure/>`_ is run as follows:

.. code::

   $ export MOLECULE_FILE=$(pwd)/molecule/preprod/molecule.yml
   $ ansible-playbook --private-key ~/.enough/enough.community/infrastructure_key \
                      --vault-password-file=~/.enough/enough.community/vault_pass.txt \
                      -i inventories/common \
                      -i ~/.enough/enough.community \
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
                    -i ~/.enough/enough.community \
                    enough-community-playbook.yml
