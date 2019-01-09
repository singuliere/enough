testinfra_hosts = ['external-host']


def test_bind(host):
    bind_host = host.get_host('ansible://bind-host',
                              ansible_inventory=host.backend.ansible_inventory)
    domain = bind_host.run("hostname -d").stdout.strip()

    cmd = host.run("getent hosts ns1.{}".format(domain))
    assert 0 == cmd.rc
    cmd = host.run("dig axfr {domain} @ns1.{domain}".format(domain=domain))
    assert 0 == cmd.rc
    # recursion is prohibited
    cmd = host.run("dig fsf.org @ns1.{domain} | grep -q '^fsf.org'".format(domain=domain))
    assert 1 == cmd.rc
