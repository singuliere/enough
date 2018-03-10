#!/bin/bash

cd /srv/securedrop/securedrop

DOCKER_RUN_ARGUMENTS='-d --name=securedrop-test -p8080:8080 -p8081:8081' ./bin/dev-shell ./bin/run
docker exec securedrop-test sudo apt-get install sqlite3
