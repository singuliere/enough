Enough
======

`cloud.enough.community <http://lab.enough.community/main/infrastructure/tree/master/molecule/enough/roles/nextcloud>`_ is installed `with docker <https://github.com/nextcloud/docker>`_.

The ``/var/lib/docker`` directory is mounted on a 3 replica volume and
should be manually backup from time to time to keep the history. If
there is not enough space, it can be resized with:

.. code::

   $ openstack volume set --size 200 cloud-volume
   $ ssh debian@cloud.enough.community
   $ sudo resize2fs /dev/sdb

Note that the ``size`` in the ansible role for the ``os_volume`` tasks
is only used when the volume is created and cannot be used to shrink
or enlarge the volume.
