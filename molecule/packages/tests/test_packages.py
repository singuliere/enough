import utils

testinfra_hosts = ['packages-host']


def test_packages(host):
    cmd = host.run("""
    docker image rm try-packages 2>/dev/null || true
    rm -fr /tmp/packages-try
    set -xe
    flock /tmp/update-packages bash -x /srv/update-packages.sh
    mkdir /tmp/packages-try
    (
       echo 'FROM ubuntu:14.04'
       echo 'RUN apt-get update'
       echo 'RUN apt-get install -y wget'
       echo 'RUN wget {url}/key.asc'
       echo 'RUN apt-key add key.asc'
       echo 'RUN apt-get install -y software-properties-common'
       echo 'RUN apt-add-repository {url}'
       echo 'RUN apt-get update'
       echo 'RUN apt-get install -y securedrop-ossec-agent'
    ) > /tmp/packages-try/Dockerfile

    docker build --tag packages-try /tmp/packages-try
    """.format(url=utils.get_address(host)))
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
