import pytest
import time
import testinfra
import yaml

testinfra_hosts = ['bind-client-host']

def test_bind(host):
    domain = host.run("hostname -d").stdout.strip()
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['bind-host']['ansible_host']
    for h in ('ns1', 'bind', 'bind-host'):
        cmd = host.run("getent hosts {}.{}".format(h, domain))
        assert 0 == cmd.rc
        assert address in cmd.stdout.strip()
        assert h + "." + domain in cmd.stdout.strip()

def test_dmarc(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("dig +short TXT _dmarc." + domain)
    assert 0 == cmd.rc
    assert "v=DMARC1" in cmd.stdout.strip()

def test_spf(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("dig +short TXT " + domain)
    assert 0 == cmd.rc
    assert "v=spf1" in cmd.stdout.strip()
