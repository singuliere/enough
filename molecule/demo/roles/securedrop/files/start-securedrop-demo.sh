#!/bin/bash

cd /srv/securedrop

# enable & compile translations
echo $(\
      echo -n 'SUPPORTED_LOCALES = ["en_US"';\
      for file in $(ls /srv/securedrop/securedrop/translations --hide messages.pot); do echo -n , \"$(basename $file)\"; done;\
      echo "]"\
      ) >> /srv/securedrop/securedrop/config.py
vagrant ssh -c '/vagrant/securedrop/manage.py translate-messages --compile' 2>/dev/null


# sleep 1 needed for magical reasons; launcher fails whithout it
vagrant ssh -c 'sudo start-stop-daemon -C --start --quiet --chuid vagrant:vagrant \
   --make-pidfile --pidfile /var/run/securedrop.pid --background --chdir /vagrant/securedrop \
   --startas /bin/bash -- -c "exec /vagrant/securedrop/manage.py run > /dev/null 2>&1 " && sleep 1' \
   2>/dev/null
