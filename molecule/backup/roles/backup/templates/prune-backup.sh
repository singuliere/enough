#!/bin/bash

source /usr/lib/backup/openrc.sh

numdays=${1:-30}
stamp1=`date --date "$numdays days ago" '+%s'`
regex="^([0-9]{4}-[0-9]{2}-[0-9]{2}).*$"
openstack ${OS_INSECURE} image list --private -f value -c Name --limit 1000 |
while read image
do
        if [[ $image =~ $regex ]] ; then
                imagedate=`echo $image | sed -r "s/$regex/\1/"`
                stamp2=`date --date "$imagedate" '+%s'`
                if [[ $stamp1 -ge $stamp2 ]] ; then
                  openstack ${OS_INSECURE} image delete $image
                fi
        fi
done
