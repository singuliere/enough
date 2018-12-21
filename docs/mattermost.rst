Mattermost
==========

`chat.enough.community <http://lab.enough.community/main/infrastructure/tree/master/molecule/chat/roles/mattermost>`_ is installed `with docker <https://docs.mattermost.com/install/prod-docker.html>`. The configuration is done `via the admin console web interface <https://chat.enough.community/admin_console>`_.

Using the CLI:

.. code::

   cd /srv/mattermost
   docker-compose -f docker-compose-infrastructure.yml exec app platform

Entering the Mattermost container:

.. code::

   cd /srv/mattermost
   docker-compose -f docker-compose-infrastructure.yml exec app sh
