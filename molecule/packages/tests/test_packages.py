import utils

testinfra_hosts = ['packages-host']


def test_packages(host):
    host.ansible("file", "dest=/tmp/packages-try state=directory", check=False)
    host.ansible("copy",
                 "dest=/tmp/packages-try/Dockerfile "
                 "src=tests/packages-dockerfile", check=False)
    cmd = host.run("""
    set -xe
    docker image rm packages-try 2>/dev/null || true
    flock /tmp/update-packages \
          bash -x /srv/update-packages.sh develop \
          >> /var/log/update-packages.log 2>&1
    sed -i -e 's|%%url%%|{url}|g' /tmp/packages-try/Dockerfile
    docker build --no-cache --tag packages-try /tmp/packages-try
    """.format(url=utils.get_address(host)))
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc

    cmd = host.run("""
    set -xe

    ! test -f /var/log/update-packages.log.1.gz
    sudo /usr/sbin/logrotate --force /etc/logrotate.d/packages-logrotate
    test -f /var/log/update-packages.log.1.gz
    test debian = $(stat --format=%U /var/log/update-packages.log)
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
