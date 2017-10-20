#!/bin/bash

source /usr/lib/backup/openrc.sh

function backup() {
    local host=$1
    local backup=$2

    openstack server image create --name $backup $host > /tmp/$host.log 2>&1 < /dev/null &
}

function wait_for_backup() {
    local host=$1
    local backup=$2

    for delay in 2 4 8 16 32 64 128 256 512 1024 ; do
        sleep $delay
        if openstack image list | grep -q $backup ; then
            break
        fi
    done
    if ! openstack image list | grep -q $backup ; then
        cat /tmp/$host.log
        echo $backup FAILED
        exit 1
    fi
}

DEFAULT_HOSTNAMES=""
{% for host in hostvars %}
{%   set vars = hostvars[host|string] %}
{%   set hostname = vars.ansible_hostname|replace('-','_') %}
DEFAULT_HOSTNAMES+={{ hostname }}
{% endfor %}

HOSTNAMES=${1:-$DEFAULT_HOSTNAMES}

for hostname in $HOSTNAMES ; do
    backup $hostname $(date +%Y-%m-%d)-$hostname
done

for hostname in $HOSTNAMES ; do
    wait_for_backup $hostname $(date +%Y-%m-%d)-$hostname
done
