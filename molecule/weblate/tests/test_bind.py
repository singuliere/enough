import pytest
import time
import testinfra
import yaml

testinfra_hosts = ['icinga_host']

def test_bind(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['weblate_host']['ansible_host']
    cmd = host.run("getent hosts weblate.securedrop.club")
    assert 0 == cmd.rc
    assert address in cmd.stdout.strip()
    assert "weblate.securedrop.club" in cmd.stdout.strip()

def test_dmarc(host):
    cmd = host.run("dig +short TXT _dmarc.securedrop.club")
    assert 0 == cmd.rc
    assert "v=DMARC1" in cmd.stdout.strip()

def test_spf(host):
    cmd = host.run("dig +short TXT securedrop.club")
    assert 0 == cmd.rc
    assert "v=spf1" in cmd.stdout.strip()

def test_dkim(host):
    cmd = host.run("dig +short TXT mail._domainkey.securedrop.club")
    assert 0 == cmd.rc
    assert "v=DKIM1" in cmd.stdout.strip()
