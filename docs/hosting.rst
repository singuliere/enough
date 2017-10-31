Hosting
=======

All virtual machines are in the OVH OpenStack cloud, under the user
**ds437901-ovh** using the `securedrop.club admin mail <admin@securedrop.club>`_.

The following OpenStack projects have been defined:

* **Contributors**
   - Region **SBG3**: all manually created VMS, before Ansible was
     introduced.
   - Region **DE1**: used for testing by Loïc Dachary
   - Region **GRA3**: used for testing by François Poulain

.. note:: the **SBG3** region will eventually be empty when all
          resources are migrated to use Ansible

* **SecureDrop**

.. note:: currently unused and reserved for CI

* **SecureDrop prod**
    - Region **SBG3**: all Ansible maintained production VMs
    - Region **DE1**: the VM running ansible to control production VMs
      in the **SBG3** region.

* `Login as a customer <https://www.ovh.com/auth/>`_
* `OpenStack OVH management <https://www.ovh.com/manager/cloud/>`_
