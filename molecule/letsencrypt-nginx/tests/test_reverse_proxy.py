testinfra_hosts = ['proxy-host']


def test_proxy(host):
    with host.sudo():
        host.run("apt-get install -y curl")
    r = host.run("curl -s -m 5 https://proxy-host.$(hostname -d)/index.html")
    assert r.rc == 0
    assert 'SOMETHING' in r.stdout
