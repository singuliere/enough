testinfra_hosts = ['weblate-host']


def test_proxy(host):
    with host.sudo():
        host.run("apt-get install -y curl")
    r = host.run("curl -s -m 5 http://weblate-host.$(hostname -d)/index.html")
    assert r.rc == 0
    assert 'SOMETHING' in r.stdout
