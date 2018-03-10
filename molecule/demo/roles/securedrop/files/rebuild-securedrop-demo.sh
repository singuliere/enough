#!/bin/bash
cd /srv/securedrop

git pull

/usr/local/bin/stop-securedrop-demo.sh

/usr/local/bin/start-securedrop-demo.sh

sudo systemctl reload nginx || true
