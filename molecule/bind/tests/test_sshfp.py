import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all:!external-host')


def test_sshfp(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("ssh -v "
                   "-o BatchMode=yes -o VerifyHostKeyDNS=yes "
                   "debian@bind-host.{} true".format(domain))
    assert "debug1: matching host key fingerprint found in DNS" in cmd.stderr
