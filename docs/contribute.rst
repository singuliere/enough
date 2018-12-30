Contribute
==========

This is the contribution guide to the `enough.community` infrastructure
which is based on Ansible. If you're a seasoned Free Software
contributor looking for a quick start, take a look at the `list of
bugs and features
<https://lab.enough.community/main/infrastructure/issues>`__,
otherwise keep reading.

.. note:: If you want to contribute to the Enoug code base, take
          a look at `the repository <https://lab.enough.community/main/app>`__. 

Resources
---------

* Repository and issue tracking: http://lab.enough.community/main/infrastructure
* Forum: https://forum.enough.community/
* Instant messenging: https://chat.enough.community/enough/
* License: `AGPLv3 <https://lab.enough.community/main/infrastructure/blob/master/LICENSE>`__
* :doc:`Who's who <team>`
* Requirement: `Integration testing`_

Bugs and features list
----------------------

Each service under the `enough.community` domain can be worked on
independently and have their own integration tests. There is no need
to understand how `Weblate` is deployed if you're improving
`Discourse`, for instance.

Organization
------------

All contributors are `organized horizontally <https://enough.community/blog/2018/07/20/manifesto/>`__

* People with access to an exclusive resource must register themselves
  in the :doc:`team directory <team>`

.. _getting_started:

Getting started
---------------

* ``git submodule update --init``
* ``apt install virtualenv``
* ``deactivate || true ; source bootstrap``
* get OpenStack credentials (ask :doc:`anyone in the <team>`) and store then in `openrc.sh`
* ``source openrc.sh``
* ``openstack server list``: should successfully return nothing on a new tenant
* ``cp clouds.yml.example clouds.yml``
* ``molecule converge -s bind``: create VMs for the scenario `bind` and run ansible playbook defined for this scenario
* ``molecule verify -s bind``: run scenario's tests
* ``molecule login -s bind --host bind-host``: should ssh to the machine
* ``molecule destroy -s bind``: destroy the virtual machine and cleanup the tenant

Ansible repository layout
-------------------------

The `ansible repository
<http://lab.enough.community/main/infrastructure/>`_ groups playbooks
and roles in separate directories to reduce the number of files to
consider when working on improving a playbook or a service.

* ``molecule/authorized_keys``: distribute SSH public keys
* ``molecule/backup``: daily VMs snapshots
* ``molecule/bind``: DNS server and client
* ``molecule/letsencrypt-nginx``: nginx reverse proxy with letsencrypt integration
* ``molecule/icinga``: resources monitoring
* ``molecule/infrastructure``: VMs creation and firewalling
* ``molecule/misc/roles/commit_etc``: keep track of changes in /etc
* ``molecule/misc/roles/history``: keep track of Ansible runs
* ``molecule/misc/roles/sexy-debian``: non essential Debian specific convenience tweaks
* ``molecule/misc/roles/sshd_config``: /etc/ssh/sshd_config shared by all VMs
* ``molecule/postfix``: outgoing mail relay for all VMs
* ``molecule/preprod``: full preproduction environment. See `Integration testing`_.
* ``molecule/sexy-debian``: optional tools that debian users like to work with

The other scenarii found in the `molecule` directory are services such
as `weblate <https://weblate.org/>`_ or `discourse <https://discourse.org/>`_.

The toplevel directory contains the `playbook that applies to the
enough.community production environment
<http://lab.enough.community/main/infrastructure/blob/master/enough-community-playbook.yml>`_. It
imports playbooks found in the `molecule` directory.

Integration testing
-------------------

Unit tests are welcome, integration tests are mandatory. When
modifying a role or a playbook in the directory `molecule/ABC` one is
expected to add a test for the new behavior and verify it runs
successfully:

* ``molecule test -s ABC``

Ansible being declarative for the most part, unit tests are only
beneficial to verify loops and conditionals work as expected. For
instance by checking a file is created only if **--tag something** is
provided. An integration test is necessary to checks if the service is
actually doing anything useful. For instance the integration tests for
weblate request that the weblate server sends a mail and
verify it is relayed by the postfix server.

When possible integration tests should be created as icinga monitoring
checks so they can be run on a regular basis in the production
environment to verify it keeps working.

After all tests pass, integration with online services must be
verified manually inside the preproduction environment.

.. note:: the person running the following commands need their
          personal ssh public key to give them access to
          `subdomain@ns1.enough.community`.

* ``molecule create -s preprod``
* ``molecule converge -s preprod``
* at end of converge you will get advertised about the testing subdomain:
  ::

        TASK [debug] *******************************************************************
            ok: [localhost] => {
            "domain": "ndi1nze0mdqk.test.enough.community"
        }

* ``molecule verify -s preprod``
* manually verify `weblate.ndi1nze0mdqk.test.enough.community`,
  `icinga.ndi1nze0mdqk.test.enough.community`, etc. and integration with online
  services such as GitHub authentication.
* ``molecule destroy -s preprod``
