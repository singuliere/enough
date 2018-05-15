import pytest

def test_apt(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("ssh-keyscan debian-host.{}".format(domain))
    assert 0 == cmd.rc
    assert 'dsa' not in cmd.stdout
    assert 'ssh-rsa' in cmd.stdout
    assert 'ssh-ed25519' in cmd.stdout
