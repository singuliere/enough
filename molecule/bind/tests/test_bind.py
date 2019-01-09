import yaml

testinfra_hosts = ['icinga-host']


def test_bind(host):
    domain = host.run("hostname -d").stdout.strip()
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['bind-host']['ansible_host']
    for h in ('ns1', 'bind', 'bind-host'):
        cmd = host.run("getent hosts {}.{}".format(h, domain))
        assert 0 == cmd.rc
        assert address in cmd.stdout.strip()
        assert h + "." + domain in cmd.stdout.strip()
        # try also with shortnames
        cmd = host.run("getent hosts {}".format(h))
        assert 0 == cmd.rc
        assert address in cmd.stdout.strip()
        assert h + "." + domain in cmd.stdout.strip()


def test_recursion(host):
    cmd = host.run("getent hosts fsf.org")
    assert 0 == cmd.rc
    assert 'fsf.org' in cmd.stdout.strip()
