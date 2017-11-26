#!/bin/bash

set -e

cd /srv/securedrop
git pull

if test "$(cat /tmp/hash)" = "$(git rev-parse HEAD)" ; then
    echo "Nothing to do"
    exit 0
fi

sudo apt-get install -y build-essential libssl-dev libffi-dev python-dev dpkg-dev git

rm -fr /srv/virtualenv
virtualenv /srv/virtualenv
source /srv/virtualenv/bin/activate
pip install -r securedrop/requirements/develop-requirements.txt

sudo apt-get install -y rsync
make build-debs

sudo apt-get install -y reprepro
reprepro -Vb /var/www/html includedeb trusty build/*.deb
rm -fr /var/www/html/{pool,dists,db}

git clean -fqqdx
git rev-parse HEAD > /tmp/hash
