def test_sshfp(host):
    if host.backend.host == "external-host":
        return
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("ssh -v -o BatchMode=yes -o VerifyHostKeyDNS=yes debian@bind-host.{} true".format(domain))
    assert "debug1: matching host key fingerprint found in DNS" in cmd.stderr
