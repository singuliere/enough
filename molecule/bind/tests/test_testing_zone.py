testinfra_hosts = ['bind-client-host', 'external-host']

def test_ns1_test(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("dig +short NS test.{}".format(domain))
    assert 0 == cmd.rc
    assert "ns1.{}.".format(domain) == cmd.stdout.strip()

def test_bind(host):
    domain = host.run("hostname -d").stdout.strip()
    cmd = host.run("getent hosts ns1.{}".format(domain))
    assert 0 == cmd.rc

def test_update(host):
    domain = host.run("hostname -d").stdout.strip()
    hostname = host.run("hostname").stdout.strip()
    host= host.get_host('ansible://bind-host', ansible_inventory=host.backend.ansible_inventory)
    cmd = host.run('''
        nsupdate <<EOF
        server localhost
        zone test.{}
        update add {}.test.{}. 1800 TXT "Updated by nsupdate ssh-ed from {}"
        show
        send
        quit
        EOF
        '''.format(domain, hostname, domain, hostname))
    assert 0 == cmd.rc

def test_dig_update(host):
    domain = host.run("hostname -d").stdout.strip()
    hostname = host.run("hostname").stdout.strip()
    cmd = host.run("dig +short TXT {}.test.{}".format(hostname, domain))
    print (cmd.stdout.strip())
    assert 0 == cmd.rc
    assert "Updated by nsupdate" in cmd.stdout.strip()

def test_clean_update(host):
    domain = host.run("hostname -d").stdout.strip()
    hostname = host.run("hostname").stdout.strip()
    host= host.get_host('ansible://bind-host', ansible_inventory=host.backend.ansible_inventory)
    cmd = host.run('''
        nsupdate <<EOF
        server localhost
        zone test.{}
        update delete {}.test.{}. TXT
        show
        send
        quit
        EOF
        '''.format(domain, hostname, domain))
    assert 0 == cmd.rc
