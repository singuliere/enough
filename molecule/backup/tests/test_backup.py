import pytest

testinfra_hosts = ['backup-host']

def expected_backups(host, count):
    cmd = host.run("""
    source /usr/lib/backup/openrc.sh
    openstack image list | grep -c weblate-host
    """)
    assert count == cmd.stdout
    print(cmd.stderr)
    assert 0 == cmd.rc
    
def test_backup(host):
    host.run("/etc/cron.daily/prune-backup 0")
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
