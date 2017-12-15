#!/bin/bash

cd /srv/securedrop

vagrant ssh -c 'pkill -P $(cat /var/run/securedrop.pid) && sudo rm -f /var/run/securedrop.pid' \
   2>/dev/null
