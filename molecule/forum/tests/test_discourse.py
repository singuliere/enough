testinfra_hosts = ['forum-host']

def test_discourse(host):
    cmd = host.run("""
    set -xe
    d=/dev/sdb
    test -e /dev/sdb || d=/dev/vda
    mount | grep $d | grep /var/lib/docker
    curl --silent https://forum.$(hostname -d) | grep --quiet 'Congratulations, you installed Discourse!'
    """)
    assert 0 == cmd.rc
