Mattermost
==========

`chat.securedrop.club <http://lab.securedrop.club/main/securedrop-club/tree/master/molecule/chat/roles/mattermost>`_ is installed `with docker <https://docs.mattermost.com/install/prod-docker.html>`_ with the `https-portal letsencrypt reverse proxy <https://github.com/SteveLTN/https-portal>`_. The configuration is done `via the admin console web interface <https://chat.securedrop.club/admin_console>`_.

Using the CLI:

.. code::

   cd /srv/mattermost
   docker-compose -f docker-compose-securedrop-club.yml exec app platform

Entering the Mattermost container:

.. code::

   cd /srv/mattermost
   docker-compose -f docker-compose-securedrop-club.yml exec app sh
