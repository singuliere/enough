testinfra_hosts = ['external-host']

def test_bind(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("getent hosts ns1.{}".format(domain))
    assert 0 == cmd.rc

def test_recursion(host):
    cmd = host.run("getent hosts fsf.org")
    assert 2 == cmd.rc
