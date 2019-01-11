def test_certs(host):
    for f in ('fakeleintermediatex1.pem', 'fakelerootx1.pem'):
        path = '/etc/ssl/certs/' + f
        if host.backend.host == "debian-host":
            expected = True  # the certs are expected to be installed
        elif host.backend.host == "bind-host":
            expected = False  # the certs are expected be installed and then removed
        assert host.exists(path) == expected
