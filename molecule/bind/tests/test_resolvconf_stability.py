import pytest
from tests.infrastructure import get_driver

testinfra_hosts = ['bind-host', 'bind-client-host']


def test_resolvconf(host):
    if get_driver() == 'docker':
        pytest.skip("docker does not do dhcp")
    resolvconf_before = host.run("cat /etc/resolv.conf").stdout.strip()
    with host.sudo():
        cmd = host.run("ifdown -a ; ifup -a")
    assert 0 == cmd.rc
    resolvconf_after = host.run("cat /etc/resolv.conf").stdout.strip()
    assert resolvconf_before == resolvconf_after
