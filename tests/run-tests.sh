#!/bin/bash

set -ex

name=enough-tox-$(date +%s)

trap "docker rm -f $name >& /dev/null || true ; docker rmi --no-prune $name >& /dev/null || true"  EXIT

(
    cat enough/common/data/base.dockerfile
    cat tests/tox.dockerfile
) | docker build --tag $name -f - .

docker run --rm --name $name -e SKIP_OPENSTACK_INTEGRATION_TESTS=true -v /var/run/docker.sock:/var/run/docker.sock $name tox
