Contribute
==========

This is the contribution guide to the `securedrop.club` infrastructure
which is based on Ansible. If you're a seasoned Free Software
contributor looking for a quick start, take a look at the `list of
bugs and features
<https://lab.securedrop.club/main/securedrop-club/issues>`__,
otherwise keep reading.

.. note:: If you want to contribute to the SecureDrop code base, take
          a look at the `SecureDrop contribution guide <https://docs.securedrop.org/en/latest/development/getting_started.html>`__. 

Resources
---------

* Repository and issue tracking: http://lab.securedrop.club/main/securedrop-club
* Forum: https://forum.securedrop.club/c/devops
* Instant messenging: https://gitter.im/freedomofpress/securedrop
* License: `AGPLv3 <https://lab.securedrop.club/main/securedrop-club/blob/master/LICENSE>`__
* :doc:`Who's who <team>`
* Requirement: `Integration testing`_

Bugs and features list
----------------------

Each service under the `securedrop.club` domain can be worked on
independantly and have their own integration tests. There is no need
to understand how `Weblate` is deployed if you're improving
`Discourse`, for instance.

* `Weblate <https://weblate.securedrop.club>`__ and its `playbook <https://lab.securedrop.club/main/securedrop-club/tree/master/molecule/weblate>`__ and `pending bugs and tasks <https://lab.securedrop.club/main/securedrop-club/issues?label_name[]=Weblate>`__
* `Discourse <https://forum.securedrop.club>`__ (no playbook yet) and `pending bugs and tasks <https://lab.securedrop.club/main/securedrop-club/issues?label_name[]=Discourse>`__
* `GitLab <https://lab.securedrop.club>`__ and its `playbook <https://lab.securedrop.club/main/securedrop-club/tree/master/molecule/gitlab>`__ and `pending bugs and tasks <https://lab.securedrop.club/main/securedrop-club/issues?label_name[]=GitLab>`__
* `Packages <https://packages.securedrop.club>`__ and its `playbook <https://lab.securedrop.club/main/securedrop-club/tree/master/molecule/packages>`__ and `pending bugs and tasks <https://lab.securedrop.club/main/securedrop-club/issues?label_name[]=Packages>`__

There are a few (and it must not grow too much) base services that
also need work (bind, postfix etc.).

* `Other elements of infrastructure <https://securedrop-club.readthedocs.io>`__ and their associated `playbooks <https://lab.securedrop.club/main/securedrop-club/tree/master/molecule>`__ and `pending bugs and tasks <https://lab.securedrop.club/main/securedrop-club/issues?label_name[]=Other>`__

Organization
------------

All contributors are organized horizontally (i.e. there is no
organization or structure) and are expected to follow these rules:

* An action that has no impact on others can be carried out without
  asking for permission
* An action impacting others is advertised in advance and carried out
  if there is a consensus
* Any person impacted by an action can call for a vote
* People with access to an exclusive resource must register themselves
  in the :doc:`team directory <team>`

.. _getting_started:

Getting started
---------------

* ``git submodule update --init``
* ``apt-get install virtualenv``
* ``deactivate || true ; source bootstrap``
* get OpenStack credentials and store then in `openrc.sh`
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
<http://lab.securedrop.club/main/securedrop-club/>`_ groups playbooks
and roles in separate directories to reduce the number of files a to
consider when working on improving a playbook or a role service.

* ``molecule/authorized_keys``: distribute SSH public keys
* ``molecule/backup``: daily VMs snapshots
* ``molecule/bind``: DNS server and client
* ``molecule/icinga``: resources monitoring
* ``molecule/infrastructure``: VMs creation and firewalling
* ``molecule/postfix``: outgoing mail relay for all VMs
* ``molecule/preprod``: full preproduction environment. See `Integration testing`_.
* ``molecule/sexy-debian``: optional tools that debian users like to work with
* ``molecule/weblate``: `weblate <https://weblate.org/>`_ for
  `securedrop.club <https://weblate.securedrop.club>`_

The toplevel directory contains the `playbook that applies to the
securedrop.club production environment
<http://lab.securedrop.club/main/securedrop-club/blob/master/securedrop-club-playbook.yml>`_. It
is a list of playbooks imported from each of the subdirectories listed
above.

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
provided.  An integration test is necessary to checks if the service
is actually working. For instance the integration tests for weblate
trigger request that the weblate server sends a mail and verify it is
relayed by the postfix mail server.

When possible integration tests should be created as icinga monitoring
checks so they can be run on a regular basis in the production
environment to verify it keeps working.

After all tests pass, integration with online services must be
verified manually inside the preproduction environment.

.. note:: the person running the following commands need their
          personal ssh public key to give them access to
          `debian@ns1.securedrop.club`.

* ``molecule create -s preprod``
* ``molecule converge -s preprod``
* at end of converge you will get advertised about the testing subdomain:
  ::

        TASK [debug] *******************************************************************
            ok: [localhost] => {
            "domain": "ndi1nze0mdqk.test.securedrop.club"
        }

* ``molecule verify -s preprod``
* manually verify `weblate.ndi1nze0mdqk.test.securedrop.club`,
  `icinga.ndi1nze0mdqk.test.securedrop.club`, etc. and integration with online
  services such as GitHub authentication.
* ``molecule destroy -s preprod``
