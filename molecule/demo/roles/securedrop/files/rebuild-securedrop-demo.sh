#!/bin/bash

cd /srv/securedrop

vagrant destroy development

git pull

vagrant up development

box_ip=$(vagrant ssh-config development | awk '$1 == "HostName" {print $2}')

sudo sed -i -e "s%proxy_pass http://192\.168\.[0-9]\+\.[0-9]\+:%proxy_pass http://$box_ip:%" /etc/nginx/sites-available/*.conf

/usr/local/bin/reset-securedrop-demo.sh

/usr/local/bin/start-securedrop-demo.sh

sudo systemctl reload nginx
