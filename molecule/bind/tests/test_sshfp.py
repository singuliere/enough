testinfra_hosts = ['bind-client-host']

def test_sshfp(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("ssh -v -o BatchMode=yes -o VerifyHostKeyDNS=yes debian@bind-host.{} true".format(domain))
    assert "matching host key fingerprint found in DNS" in cmd.stderr
