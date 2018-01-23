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
    flock /tmp/update-packages bash -x /srv/update-packages.sh
    sed -i -e 's|%%url%%|{url}|g' /tmp/packages-try/Dockerfile
    docker build --no-cache --tag packages-try /tmp/packages-try
    """.format(url=utils.get_address(host)))
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
