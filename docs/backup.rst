Backups and recovery
====================

Backup policy
-------------

Each VM is `snapshoted daily <http://lab.securedrop.club/main/securedrop-club/blob/master/molecule/backup/roles/backup/templates/backup.sh>`_ and snapshots `older than 30 days <http://lab.securedrop.club/main/securedrop-club/blob/master/molecule/backup/roles/backup/templates/prune-backup.sh>`_ are removed.

Disaster recovery
-----------------

The VMs are cheap and do not provide any kind of guarantee and all
data can be lost. To recover a lost production VM:

* login debian@ansible.securedrop.club and get OpenStack credentials from `~/openrc.sh` or :doc:`ask a team member <team>`.
* login to `the horizon panel <https://horizon.cloud.ovh.net/>`_ and boot the latest snapshot
* :doc:`run ansible <ansible>` so the DNS updates with the IP of the newly created VM
