testinfra_hosts = ['bind-client-host']

def test_caa(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("dig +short CAA " + domain)
    assert 0 == cmd.rc
    assert '"letsencrypt.org"' in cmd.stdout.strip()
