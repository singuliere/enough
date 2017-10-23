import pytest
import time
import testinfra
import yaml

testinfra_hosts = ['bind-client-host']

def test_bind(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['bind-host']['ansible_host']
    cmd = host.run("getent hosts ns1.securedrop.club")
    assert 0 == cmd.rc
    assert address in cmd.stdout.strip()
    assert "ns1.securedrop.club" in cmd.stdout.strip()

def test_dmarc(host):
    cmd = host.run("dig +short TXT _dmarc.securedrop.club")
    assert 0 == cmd.rc
    assert "v=DMARC1" in cmd.stdout.strip()

def test_spf(host):
    cmd = host.run("dig +short TXT securedrop.club")
    assert 0 == cmd.rc
    assert "v=spf1" in cmd.stdout.strip()
