testinfra_hosts = ['postfix-client-host']


def test_dmarc(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("dig +short TXT _dmarc." + domain)
    assert 0 == cmd.rc
    assert "v=DMARC1" in cmd.stdout.strip()

def test_spf(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("dig +short TXT " + domain)
    assert 0 == cmd.rc
    assert "v=spf1" in cmd.stdout.strip()

def test_dkim(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("dig +short TXT mail._domainkey." + domain)
    assert 0 == cmd.rc
    assert "v=DKIM1" in cmd.stdout.strip()
