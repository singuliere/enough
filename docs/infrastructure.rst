.. _infrastructure:

Hosting and infrastructure
==========================

OpenStack at OVH
----------------

All virtual machines are in the OVH OpenStack cloud, under the user
**ds437901-ovh** using the `securedrop.club admin mail <admin@securedrop.club>`_.

The following OpenStack projects have been defined:

* **Contributors**
   - Region **GRA3**: all manually created VMS, before Ansible was
     introduced.
   - Region **DE1**: used for testing by Loïc Dachary
   - Region **SBG3**: used for testing by François Poulain

.. note:: the **GRA3** region will eventually be empty when all
          resources are migrated to use Ansible

* **SecureDrop**

.. note:: currently unused and reserved for CI

* **SecureDrop prod**
    - Region **SBG3**: all Ansible maintained production VMs
    - Region **DE1**: the VM running ansible to control production VMs
      in the **SBG3** region.

* `Login as a customer <https://www.ovh.com/auth/>`_
* `OpenStack OVH management <https://www.ovh.com/manager/cloud/>`_

Security groups
---------------

The firewall to all machines is based on `openstack security groups
<https://docs.openstack.org/nova/latest/admin/security-groups.html>`_. The
`securedrop-club
<http://lab.securedrop.club/main/securedrop-club/blob/master/molecule/infrastructure/roles/vm/tasks/main.yml>`_
security group is shared by all VMs. It means that if the DNS VM needs
to open port 53/udp, it will be open for all VMs. This was done
because it is simpler but a distinct set of rules for each VM would be better.

VM naming conventions
---------------------

All VMs names end with `-host` because it makes them easier to grep.

Global account name
-------------------

The `debian` account exists on all VMs and is used by all for
configuration and debug.

