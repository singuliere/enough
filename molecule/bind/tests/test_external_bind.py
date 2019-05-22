from tests.infrastructure import get_driver

testinfra_hosts = ['external-host']


def test_bind_external(host):
    bind_host = host.get_host('ansible://bind-host',
                              ansible_inventory=host.backend.ansible_inventory)
    domain = bind_host.run("hostname -d").stdout.strip()
    address = bind_host.ansible.get_variables()['ansible_host']

    infrastructure = get_driver()

    if infrastructure == 'openstack':
        cmd = host.run(f"dig ns1.{domain}")
        print(cmd.stdout)
        print(cmd.stderr)
        assert 0 == cmd.rc

    cmd = host.run(f"dig axfr {domain} @{address}")
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
    # recursion is prohibited
    cmd = host.run(f"dig fsf.org @{address} | grep -q '^fsf.org'")
    print(cmd.stdout)
    print(cmd.stderr)
    assert 1 == cmd.rc
