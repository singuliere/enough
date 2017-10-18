import pytest
import time
import testinfra
import yaml

testinfra_hosts = ['bind_client_host']

def test_bind(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['bind_host']['ansible_host']
    cmd = host.run("getent hosts ns1.securedrop.club")
    assert 0 == cmd.rc
    assert address in cmd.stdout.strip()
    assert "ns1.securedrop.club" in cmd.stdout.strip()
