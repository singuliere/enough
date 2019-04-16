#!/bin/bash

# install letsencrypt certs when/if they are mounted at /usr/local/share/ca-certificates
# see also molecule/letsencrypt/roles/letsencrypt/tasks/main.yml
update-ca-certificates
