testinfra_hosts = ['cloud-host']

def test_nextcloud(host):
    cmd = host.run("""
    set -xe
    mount | grep /dev/sdb | grep /var/lib/docker
    curl --silent http://127.0.0.1/ | grep -i nextcloud
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
