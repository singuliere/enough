def test_ssh(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("ssh-keyscan debian-host.{}".format(domain))
    assert 0 == cmd.rc
    assert 'ssh-rsa' in cmd.stdout
    assert 'ssh-ed25519' in cmd.stdout
