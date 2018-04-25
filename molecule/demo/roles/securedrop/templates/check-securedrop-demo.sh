#!/bin/bash

set -e

: ${NAME:={{ demo_name }}}
: ${SOURCE_PORT:={{ base_port + 80 }}}
: ${JOURNALIST_PORT:={{ base_port + 81 }}}
: ${USER:={{ ansible_user }}}

cd ${NAME}

function stop_demo() {
    docker rm -f securedrop-${NAME} || true
}

function start_demo() {
    local i18n_tool
    if test -f securedrop/i18n_tool.py ; then
        i18n_tool=i18n_tool
    else
        i18n_tool=manage
    fi
    sed -i -e "s/securedrop-test/securedrop-${NAME}/" securedrop/bin/dev-shell
    DOCKER_RUN_ARGUMENTS="-d --name=securedrop-${NAME} -p${SOURCE_PORT}:8080 -p${JOURNALIST_PORT}:8081" securedrop/bin/dev-shell ./bin/run
    securedrop/bin/dev-shell ./$i18n_tool.py --verbose translate-messages --compile
    git checkout securedrop/bin/dev-shell
    docker exec securedrop-${NAME} sudo apt-get install sqlite3
    git apply 0001-demo-notice.patch --3way
    sudo chown -R ${USER} .
    get_credentials_sum > credentials-sum-${NAME}.txt
}

function rebuild_demo() {
    git reset --hard
    git pull
    stop_demo
    start_demo
    sudo systemctl reload nginx
}

function check_ports() {
    timeout 30 curl -s 127.0.0.1:${SOURCE_PORT} &&
        timeout 30 curl -s 127.0.0.1:${JOURNALIST_PORT}
}

function wait_ports() {
    for d in 2 4 8 16 32 64 128 256 512 ; do
        if check_ports ; then
            break
        fi
        sleep $d
    done
    check_ports
}

function get_credentials_sum() {
    docker exec securedrop-${NAME} sqlite3 /var/lib/securedrop/db.sqlite "select username,pw_salt,pw_hash,is_admin,otp_secret,is_totp,hotp_counter from journalists where id = 1" | sha1sum
}

function check_credentials() {
    test "$(get_credentials_sum)" = "$(cat credentials-sum-${NAME}.txt)"
}

function check_demo() {
    if ! check_ports || ! check_credentials ; then
        rebuild_demo
        wait_ports || return 1
    fi
}

${1:-check_demo}

