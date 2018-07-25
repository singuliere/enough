testinfra_hosts = ['cloud-host', 'wereport-host']

def test_nextcloud(host):
    cmd = host.run("""
    set -xe
    d=/dev/sdb
    test -e /dev/sdb || d=/dev/vda
    mount | grep $d | grep /var/lib/docker
    curl --silent http://127.0.0.1/login | grep --quiet 'Forgot pass'
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc

def test_nextcloud_via_tor(host):
    cmd = host.run("""
    set -xe
    hostname=$(sudo cat /var/lib/tor/services/cloud/hostname)
    torsocks curl --silent http://$hostname/login | grep --quiet 'Forgot pass'
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc