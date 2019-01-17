Ansible
=======

Secrets
-------

The default credentials (for Weblate, Discourse etc.) are only
suitable for integration testing and must be overriden before
deploying on publicly available hosts. The recommended way of doing this is to:

* fork The `ansible repository <http://lab.enough.community/main/infrastructure/>`_ into a private repository
* add files overriding the secrets in `inventories/common/{host,group}_vars/*/*secrets*.yml`
* encrypt those files with `ansible vault <https://docs.ansible.com/ansible/latest/user_guide/vault.html>`_
* share the password to decrypt the files with trusted administrators

The encrypted secrets are kept in a private repository to not be
publicly exposed to brute force attacks.

Getting the production repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code::

   $ git clone --recursive \
               git@lab.enough.community:main/production-infrastructure.git
   $ cd infrastructure
   $ git remote add upstream \
               git@lab.enough.community:main/infrastructure.git
   $ ansible-vault decrypt \
                   --vault-password-file ~/.vault_pass.txt \
                   infrastructure_key

Rebasing production
~~~~~~~~~~~~~~~~~~~

.. code::

   $ git rebase upstream/master

Pushing to production
~~~~~~~~~~~~~~~~~~~~~

.. code::

   $ git push --force origin master

Running
-------

Creating new hosts
~~~~~~~~~~~~~~~~~~

.. code::

   ANSIBLE_VAULT_PASSWORD_FILE=$HOME/.vault_pass.txt \
      molecule create -s preprod

It will create the `inventories/01-hosts.yml` file, from which the new
hosts can be copy/pasted into `inventories/common/hosts-definition.yml`
or `inventories/dachary/hosts-definition.yml` etc.

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
<http://lab.enough.community/main/infrastructure/>`_ is run from the
`/srv/checkout` directory of the `ansible.enough.community` virtual
machine as follows:

.. code::

   ansible-playbook --private-key infrastructure_key \
                    --vault-password-file=$HOME/.vault_pass.txt \
                    -i inventories/common \
                    enough-community-playbook.yml

Some hosts contain private information that belong to users who only
trust some administrators of the infrastructure, not all of
them. These hosts only have the ssh public keys of the trusted
administrators and are listed in a dedicated inventory subdirectory.
For instance, the administrator `dachary` owns the the inventory
directory `inventories/dachary`. This administrator can then run the
playbook on all the common infrastructure as well as all the hosts
that can only be accessed by them as follows:

.. code::

   ansible-playbook --private-key ~/.ssh/id_rsa \
                    --vault-password-file=$HOME/.vault_pass.txt \
                    -i inventories/common \
                    -i inventories/dachary \
                    enough-community-playbook.yml

Inventory
---------

The ansible inventory is created by the
``molecule/infrastructure/create.yml`` playbook and stored in the
``inventories/01-hosts.yml`` file every time the ``molecule create``
command runs.  The inventory variables (such as the ssh port number)
are read from the ``hosts-base.yml`` file.

It is the responsibility of the system administrator to copy/paste the
content of ``inventories/01-hosts.yml`` in the relevant subdirectory
(`common` etc.).

Updating
--------

The `/srv/checkout` directory is a clone of the `ansible repository
<http://lab.enough.community/main/infrastructure/>`_ and can be updated with:

.. code::

   git pull --rebase
