#!/bin/bash

set -e

: ${NAME:={{ demo_name }}}
: ${SOURCE_PORT:={{ base_port + 80 }}}
: ${JOURNALIST_PORT:={{ base_port + 81 }}}
: ${USER:={{ ansible_user }}}
: ${BRANCH:={{ branch }}}

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
    DOCKER_RUN_ARGUMENTS="--interactive=false" securedrop/bin/dev-shell ./$i18n_tool.py --verbose translate-messages --compile
    # remove this line once https://github.com/freedomofpress/securedrop/pull/3398/files is in the stable release i.e. after 0.8.0 is published
    DOCKER_RUN_ARGUMENTS="--interactive=false" securedrop/bin/dev-shell mkdir -p /var/lib/securedrop/tmp
    git checkout securedrop/bin/dev-shell
    docker exec securedrop-${NAME} sudo apt-get install sqlite3
    git apply 0001-demo-notice.patch --3way
    #
    # We want all known languages for the demo, no matter how incomplete they are
    #
    local sl=$(ls securedrop/translations/ | grep -v messages.pot | while read l ; do echo -n "'$l', " ; done)
    sed -i -e "s/^SUPPORTED_LOCALES.*/SUPPORTED_LOCALES = [$sl 'en_US']/" securedrop/config.py
    sudo chown -R ${USER} .
    get_credentials_sum > credentials-sum-${NAME}.txt
}

function setup_entropy() {
    # securedrop/source_app/main.py::submit needs get_entropy_estimate() > 2400
    # haveged can provide that quickly but it will only wake up when
    # /proc/sys/kernel/random/entropy_avail drops below
    # /proc/sys/kernel/random/write_wakeup_threshold. By setting
    # /proc/sys/kernel/random/write_wakeup_threshold to a value greater than
    # 2400 we ensure there will always be more than 2400 in
    # /proc/sys/kernel/random/entropy_avail thanks to haveged.
    # The value must not be too high otherwise it will consume a lot of CPU power.
    # Experience shows 4096 requires a CPU core at all times.
    sudo bash -c "echo 3000 > /proc/sys/kernel/random/write_wakeup_threshold"
}

function rebuild_demo() {
    sudo git clean -qffdx securedrop
    git reset --hard
    git pull
    setup_entropy
    stop_demo
    start_demo
    sudo systemctl reload nginx
}

function check_ports() {
    timeout 30 curl -s 127.0.0.1:${SOURCE_PORT} > /dev/null &&
        timeout 30 curl -s 127.0.0.1:${JOURNALIST_PORT} > /dev/null
}

function repo_up_to_date() {
    git fetch
    git diff --quiet origin/${BRANCH}..
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
    if ! repo_up_to_date || ! check_ports || ! check_credentials ; then
        rebuild_demo
        wait_ports || return 1
    fi
}

${1:-check_demo}
