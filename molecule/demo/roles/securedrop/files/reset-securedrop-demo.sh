#!/bin/bash

cd /srv/securedrop

vagrant ssh -c 'rm -r /var/lib/securedrop/*'

vagrant ssh -c 'cd /var/lib/ && sudo tar xf /vagrant/var-lib-securedrop.tar.gz'
