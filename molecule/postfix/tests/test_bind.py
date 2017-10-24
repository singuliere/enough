testinfra_hosts = ['postfix-client-host']

def test_dkim(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("dig +short TXT mail._domainkey." + domain)
    assert 0 == cmd.rc
    assert "v=DKIM1" in cmd.stdout.strip()
