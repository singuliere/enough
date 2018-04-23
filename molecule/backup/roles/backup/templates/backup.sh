#!/bin/bash

source /usr/lib/backup/openrc.sh

function backup() {
    local host=$1
    local backup=$2

    openstack ${OS_INSECURE} server image create --name $backup $host > /tmp/$host.log 2>&1 < /dev/null &
}

function image_active() {
    local backup=$1
    openstack ${OS_INSECURE} image list --private -c Name -c Status -f value | grep -q "$backup active"
}

function wait_for_backup() {
    local host=$1
    local backup=$2

    for delay in 2 4 8 16 32 64 128 256 512 1024 ; do
        sleep $delay
        if image_active $backup ; then
            break
        fi
    done
    if ! image_active $backup ; then
        cat /tmp/$host.log
        echo $backup FAILED
        exit 1
    fi
}

DEFAULT_HOSTNAMES=""
{% for host in groups['pets'] %}
DEFAULT_HOSTNAMES+="{{ host }} "
{% endfor %}

HOSTNAMES=${1:-$DEFAULT_HOSTNAMES}

for hostname in $HOSTNAMES ; do
    backup $hostname $(date +%Y-%m-%d)-$hostname
done

for hostname in $HOSTNAMES ; do
    wait_for_backup $hostname $(date +%Y-%m-%d)-$hostname
done
