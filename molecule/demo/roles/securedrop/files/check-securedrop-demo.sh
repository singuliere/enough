#!/bin/bash

cd /srv/securedrop
box_ip=127.0.0.1

# test if curl didn't answered correctly

if ! timeout 30 curl -s $box_ip:8080 2>&1 > /dev/null
then
    echo should rebuild demo
    /usr/local/bin/rebuild-securedrop-demo.sh
    exit
fi

if ! timeout 30 curl -s $box_ip:8081 2>&1 > /dev/null
then
    echo should rebuild demo
    /usr/local/bin/rebuild-securedrop-demo.sh
    exit
fi

# test if journalist credentials has been changed

sha1="600f178418538fb90b18a9e83fe826e1d17753bd"
if ! docker exec securedrop-test sqlite3 /var/lib/securedrop/db.sqlite "select id,username,pw_salt,pw_hash,is_admin,otp_secret,is_totp,hotp_counter,created_on from journalists" | sha1sum  2>/dev/null | grep -q $sha1
then
    echo should reset credentials
    /usr/local/bin/stop-securedrop-demo.sh
    /usr/local/bin/start-securedrop-demo.sh
    exit
fi
