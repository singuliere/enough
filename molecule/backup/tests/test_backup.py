testinfra_hosts = ['bind-host']


def expected_backups(host, count):
    cmd = host.run("""
    . /usr/lib/backup/openrc.sh
    openstack ${OS_INSECURE} image list | grep -c weblate-host
    """)
    print(cmd.stderr)
    assert count == cmd.stdout
    assert 0 == cmd.rc


def test_backup(host):
    # we need --insecure during tests otherwise going back in time a few days
    # may invalidate some certificates and result in errors such as:
    # SSL exception connecting to
    #    https://auth.cloud.ovh.net/v2.0/tokens: [SSL: CERTIFICATE_VERIFY_FAILED]
    with host.sudo():
        cmd = host.run("echo export OS_INSECURE=--insecure >> /usr/lib/backup/openrc.sh")
        print(cmd.stdout)
        print(cmd.stderr)
        assert 0 == cmd.rc
    cmd = host.run("/etc/cron.daily/prune-backup 0")
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
    try:
        with host.sudo():
            host.run("timedatectl set-ntp 0")
            cmd = host.run("""
            set -x
            date -s '-15 days'
            bash -x /etc/cron.daily/backup
            date -s '-30 days'
            bash -x /etc/cron.daily/backup
            """)
            host.run("timedatectl set-ntp 1")
        print(cmd.stdout)
        print(cmd.stderr)
        assert 0 == cmd.rc
        expected_backups(host, '2')
        host.run("bash -x /etc/cron.daily/prune-backup 30")
        expected_backups(host, '1')
    finally:
        host.run("timedatectl set-ntp 1")
        host.run("bash -x /etc/cron.daily/prune-backup 0")
