import pytest
import time
import testinfra
import yaml

def test_bind(host):
    domain = host.run("hostname -d").stdout.strip()
    inventory = yaml.load(open(host.backend.ansible_inventory))
    for h in ['ns1', 'postfix', 'ansible'] + inventory['all']['hosts'].keys():
        cmd = host.run("getent hosts {}.{}".format(h, domain))
        assert 0 == cmd.rc
        assert h + "." + domain in cmd.stdout.strip()

def test_recursion(host):
    cmd = host.run("getent hosts fsf.org")
    assert 0 == cmd.rc
    assert 'fsf.org' in cmd.stdout.strip()
