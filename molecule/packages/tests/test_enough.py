testinfra_hosts = ['packages-host']

def test_enough(host):
    cmd = host.run("""
    set -xe
    flock /tmp/update-packages \
          bash -x /srv/enough-android-update-packages.sh
    test -f /var/www/html/enough.apk
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
