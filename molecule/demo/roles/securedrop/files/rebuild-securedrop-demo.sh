#!/bin/bash
cd /srv/securedrop

git pull

if vagrant status development |& grep running ; then
   sudo reboot
else
   vagrant up development

   /usr/local/bin/reset-securedrop-demo.sh

   /usr/local/bin/start-securedrop-demo.sh

   sudo systemctl reload nginx
fi
