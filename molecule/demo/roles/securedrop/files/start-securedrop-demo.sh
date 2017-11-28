#!/bin/bash

cd /srv/securedrop

# sleep 1 needed for magical reasons; launcher fails whithout it
vagrant ssh -c 'sudo start-stop-daemon -C --start --quiet --chuid vagrant:vagrant \
   --make-pidfile --pidfile /var/run/securedrop.pid --background --chdir /vagrant/securedrop \
   --startas /bin/bash -- -c "exec /vagrant/securedrop/manage.py run > /dev/null 2>&1 " && sleep 1'
