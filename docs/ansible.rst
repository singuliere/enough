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
`/srv/checkout/inventory/host_vars/` (so that the default used during
testing are not used in production).

.. code::

   $ echo with_https: true | sudo tee /srv/checkout/inventory/group_vars/all/with_https.yml
   $ echo domain: enough.community | sudo tee /srv/checkout/inventory/group_vars/all/domain.yml

Running
-------

The `ansible repository
<http://lab.enough.community/main/enough-community/>`_ is run from the
`/srv/checkout` directory of the `ansible.enough.community` virtual
machine as follows:

.. code::

   ansible-playbook --private-key infrastructure_key \
                    -i inventory \
                    enough-community-playbook.yml

Inventory
---------

The ansible inventory is created by the
``molecule/infrastructure/create.yml`` playbook and stored in the
``inventory/01-hosts.yml`` file every time the ``molecule create -s
preprod`` command runs.  The inventory variables (such as the ssh port
number) are read from the ``hosts-base.yml`` file.

Updating
--------

The `/srv/checkout` directory is a clone of the `ansible repository
<http://lab.enough.community/main/infrastructure/>`_ and can be updated with:

.. code::


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
   git pull --rebase
