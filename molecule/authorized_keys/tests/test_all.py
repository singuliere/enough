import sh


def test_all(host):
    address = host.ansible.get_variables()['ansible_host']
    marker = "MARKER"
    key = 'roles/authorized_keys/files/test_keys/testkey'
    sh.chmod('600', key)
    r = sh.ssh('-i', key, 'debian@' + address, 'echo', marker)
    assert r.stdout.decode('utf-8').strip() == marker
