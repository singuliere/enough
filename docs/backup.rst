Backups and recovery
====================

Backup policy
-------------

Each VM is `snapshoted daily <http://lab.enough.community/main/infrastructure/blob/master/molecule/backup/roles/backup/templates/backup.sh>`_ and snapshots `older than 30 days <http://lab.enough.community/main/infrastructure/blob/master/molecule/backup/roles/backup/templates/prune-backup.sh>`_ are removed.

Disaster recovery
-----------------

The VMs are cheap and do not provide any kind of guarantee: all
data they contain can be lost. To recover a lost production VM:

* login debian@ansible.enough.community and get OpenStack credentials from `~/openrc.sh` or :doc:`ask a team member <team>`.
* cd /srv/checkout

If the virtual machine is cattle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Delete the broken machine if it is still around, e.g. ``openstack stack delete website-host``
* Create the machine again `as if it was new <ansible>`__
* :doc:`Run ansible <ansible>` so the DNS updates with the IP of the newly created VM

If the virtual machine is a pet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Get the name of the latest backup with ``openstack image list --private``
* Rename the broken machine if it is still around, e.g. ``openstack server set --name packages-destroyed packages-host``
* Get the flavor for the machine from ``molecule/preprod/molecule.yml``
* Create a new machine from the backup, e.g. ``openstack server create --flavor s1-2 --image 2018-05-14-packages-host --security-group infrastructure --wait packages-host``
* Edit ``inventories/common/01-hosts.yml`` and replace the IP of the broken machine with the IP of the new machine
* Clear the ansible cache ``rm -fr ~/.ansible``
* :doc:`Run ansible <ansible>` so the DNS updates with the IP of the newly created VM
* Reboot the machine, in case it had IPs from before the DNS was updated by ansible
* :doc:`Run ansible <ansible>` so the DNS updates with the IP of the newly created VM

Disaster recover exercize
-------------------------

If the virtual machine is cattle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Remove the machine, e.g. ``openstack server delete website-host``

If the virtual machine is a pet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Rename the machine, e.g. ``openstack server set --name packages-destroyed packages-host``
* Suspend, e.g. ``openstack server suspend packages-destroyed``
* Remove the machine when the recovery is successfull, e.g. ``openstack server remove packages-destroyed``
