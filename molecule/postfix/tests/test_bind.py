testinfra_hosts = ['postfix-client-host']

def test_dkim(host):
    cmd = host.run("dig +short TXT mail._domainkey.securedrop.club")
    assert 0 == cmd.rc
    assert "v=DKIM1" in cmd.stdout.strip()
