Ansible
=======

Creation
--------

The `ansible.enough.community` virtual machine was created in the `GRA5` region with:

.. code::

   $ openstack keypair create --public-key ~/.ssh/id_rsa.pub loic
   $ openstack --quiet server create --image 'Debian 9' --flavor 's1-2' \
             --key-name loic --wait ansible
   $ scp enough-openrc-production.sh debian@ansible.enough.community:openrc.sh
   $ ssh debian@ansible.enough.community
   $ sudo apt-get update
   $ sudo apt-get install tmux emacs-nox git python-openstackclient rsync virtualenv python-all-dev
   $ sudo chown debian /srv
   $ rsync -av enough-community/ debian@ansible.enough.community:/srv/enough-community/
   $ ( cd /srv/enough-community && git submodule update )
   $ 
   $ virtualenv /srv/virtualenv
   $ cat >> .bashrc <<EOF
   source /srv/virtualenv/bin/activate
   source $HOME/openrc.sh
   export HISTSIZE=1000000
   export PROMPT_COMMAND='history -a' # history -r
   EOF

Logout and login again:

.. code::

   $ pip install -r /srv/enough-community/requirements.txt
   $ ssh-keygen -f infrastructure_key
   $ cat > /srv/enough-community/private-key.yml <<EOF
   ---
   ssh_private_keyfile: "{{ lookup('pipe', 'git rev-parse --show-toplevel') }}/infrastructure_key"
   EOF

Manually create `/srv/enough-community/clouds.yml` from `~/openrc.sh` and check it works:

.. code::

   $ molecule create -s infrastructure
   $ molecule destroy -s infrastructure

Set the passwords and other secret credentialis in the file or
directory matching a given host at
`/srv/checkout/inventories/common/host_vars/` (so that the default used during
testing are not used in production).

.. code::

   $ echo domain: enough.community | sudo tee /srv/checkout/inventories/common/group_vars/all/domain.yml

Secrets
-------

The default credentials (for Weblate, Discourse etc.) are only
suitable for integration testing and must be overriden before
deploying on publicly available hosts. The recommended way of doing this is to:

* fork The `ansible repository <http://lab.enough.community/main/infrastructure/>`_ into a private repository
* add files overriding the secrets in `inventories/common/host_vars/*/secrets.yml`
* encrypt those files with `ansible vault <https://docs.ansible.com/ansible/latest/user_guide/vault.html>`_
* share the password to decrypt the files with trusted administrators

The encrypted secrets are kept in a private repository to not be
publicly exposed to brute force attacks.

Running
-------

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
