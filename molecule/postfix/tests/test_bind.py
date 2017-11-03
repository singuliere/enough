testinfra_hosts = ['postfix-client-host']

def test_spf(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("dig +short TXT " + domain)
    assert 0 == cmd.rc
    assert "v=spf1" in cmd.stdout.strip()
