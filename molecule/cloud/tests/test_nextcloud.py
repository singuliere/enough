testinfra_hosts = ['cloud-host']

def test_nextcloud(host):
    cmd = host.run("""
    set -xe
    d=/dev/sdb
    test -e /dev/sdb || d=/dev/vda
    mount | grep $d | grep /var/lib/docker
    curl --silent http://127.0.0.1/login | grep --quiet -i 'Forgot pass'
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc

def test_nextcloud_via_tor(host):
    cmd = host.run("""
    set -x
    sudo apt-get install -y torsocks
    for d in 2 4 8 16 32 64 128 256 512 ; do
      hostname=$(sudo cat /var/lib/tor/services/cloud/hostname)
      torsocks curl --silent http://$hostname/ | grep --quiet -i nextcloud && break
      sleep $d
    done
    torify curl --silent http://$hostname/ | grep --quiet -i nextcloud
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
