.. _infrastructure:

Hosting and infrastructure
==========================

OpenStack at OVH
----------------

All virtual machines are in the OVH OpenStack cloud. The OVH account
is **ce188933-ovh** (login via https://www.ovh.com/auth/) and is bound
to the `enough.community admin mail <admin@enough.community>`_.

The following OVH projects have been defined:

.. note::
   The OVH user is the paying customer and the OVH projects are
   completely isolated from each other. The OVH interface allows to
   create OpenStack tenants in a given project. An OpenStack tenant
   only has access to the OVH project in which it has been created.
   A tenant has access to all the regions.

* **OVH Project: Contributors**
   - Region **GRA5**: used for testing by Loïc Dachary
   - Region **SBG5**: used for testing by François Poulain

* **OVH Project: CI**
   - Region **DE1**: GitLab runner

* **OVH Project: Production**
   - Region **GRA5**: all Ansible maintained production VMs

The OVH acount **cl283532-ovh** is dedicated to hosting Enough
instances dedicated to an organization or an individual.

* `Login as a customer <https://www.ovh.com/auth/>`_
* `OpenStack OVH management <https://www.ovh.com/manager/cloud/>`_

.. _firewall:

Security groups
---------------

The firewall to all machines is based on `openstack security groups
<https://docs.openstack.org/nova/latest/admin/security-groups.html>`_. There
is one `security group per VM
<http://lab.enough.community/main/infrastructure/blob/master/molecule/infrastructure/roles/vm/tasks/main.yml>`_.

VM naming conventions
---------------------

All VMs names end with `-host` because it makes them easier to grep.

Global account name
-------------------

The `debian` account exists on all VMs and is used by all for
configuration and debug.

