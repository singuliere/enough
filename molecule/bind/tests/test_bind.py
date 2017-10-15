import pytest
import time
import testinfra
import yaml


def test_bind(host):
    if host.backend.host != 'bind_client_host':
        pytest.skip("only run on bind_client_host")

    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['bind_host']['ansible_host']
    cmd = host.run("getent hosts ns1.test.securedrop.club")
    assert 0 == cmd.rc
    assert address + "   ns1.test.securedrop.club" == cmd.stdout.strip()
