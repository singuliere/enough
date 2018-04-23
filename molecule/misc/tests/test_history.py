import pytest
import testinfra

def test_hosts_vars(host):
    hostname = host.run("hostname -s").stdout
    cmd = host.run('grep -q {} /etc/securedrop-club/hosts_vars'.format(hostname))
    assert 0 == cmd.rc

def test_history(host):
    root = "fc72e23"
    cmd = host.run('grep -q {} /etc/securedrop-club/history'.format(root))
    assert 0 == cmd.rc
