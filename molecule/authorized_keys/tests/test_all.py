from io import StringIO
import sh


def test_all(host):
    address = host.ansible.get_variables()['ansible_host']
    marker = "MARKER"
    result = StringIO()
    key = 'roles/authorized_keys/files/test_keys/testkey'
    sh.chmod('600', key)
    sh.ssh('-i', key, 'debian@' + address, 'echo', marker, _out=result)
    assert result.getvalue().strip() == marker
