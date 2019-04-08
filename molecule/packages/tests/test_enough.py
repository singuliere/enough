import os

testinfra_hosts = ['packages-host']


def test_enough_android(host):
    cmd = host.run("""
    set -xe
    flock /tmp/update-packages \
          bash -x /srv/enough-android-update-packages.sh
    test -f /usr/share/nginx/html/enough.apk
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc


def test_enough_pip(host):
    r = host.ansible("file", "path=/tmp/docker state=directory", check=False)
    print(str(r))
    current_dir = os.path.dirname(os.path.abspath(__file__))
    r = host.ansible("copy",
                     "dest=/tmp/docker/Dockerfile "
                     "src={d}/../../../enough/common/data/base.dockerfile".format(d=current_dir),
                     check=False)
    print(str(r))
    assert host.file("/tmp/docker/Dockerfile").exists
    cmd = host.run("""
    set -xe
    cd /tmp/docker
    cp -a /usr/share/nginx/html/enough/*.tar.gz .
    echo 'COPY *.tar.gz ./' >> Dockerfile
    echo 'RUN /opt/venv/bin/pip install *.tar.gz' >> Dockerfile
    docker build -t enough .
    docker run --rm enough enough --help
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
