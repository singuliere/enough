#!/bin/bash

cd /srv/securedrop
box_ip=$(vagrant ssh-config development | awk '$1 == "HostName" {print $2}')

# test if curl didn't answered correctly

if ! timeout 30 curl -s $box_ip:8080 2>&1 > /dev/null
then
    echo should rebuild demo
    if pgrep -f rebuild-securedrop-demo >/dev/null
    then
        echo already rebuilding
        exit
    fi
    /usr/local/bin/rebuild-securedrop-demo.sh
    exit
fi

if ! timeout 30 curl -s $box_ip:8081 2>&1 > /dev/null
then
    echo should rebuild demo
    if pgrep -f rebuild-securedrop-demo >/dev/null
    then
        echo already rebuilding
        exit
    fi
    /usr/local/bin/rebuild-securedrop-demo.sh
    exit
fi

# test if journalist credentials has been changed

sha1="ec5b64969bc6f3d74621810bf61e697f1431ca75"
if ! vagrant ssh -c 'sqlite3 /var/lib/securedrop/db.sqlite "select id,username,pw_salt,pw_hash,is_admin,otp_secret,is_totp,hotp_counter,created_on from journalists" | sha1sum'  2>/dev/null | grep -q $sha1
then
    echo should reset credentials
    /usr/local/bin/stop-securedrop-demo.sh
    /usr/local/bin/reset-securedrop-demo.sh
    /usr/local/bin/start-securedrop-demo.sh
    exit
fi

# test if upstream repo has been updated
# if things go wrong, demo will be rebuilt at next run
git fetch
if test "$(git log --oneline origin/master..)"
then
    echo should pull and restart
    /usr/local/bin/stop-securedrop-demo.sh
    git pull
    /usr/local/bin/start-securedrop-demo.sh
    exit
fi
