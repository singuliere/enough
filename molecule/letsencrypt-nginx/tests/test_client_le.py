testinfra_hosts = ['client-host']

def test_certs(host):
    with host.sudo():
        host.run("apt-get install -y curl")
    assert host.run("curl -m 5 -I https://nginx-host.$(hostname -d)").rc == 0
    assert host.run("curl -m 5 -I https://bind-host.$(hostname -d)").rc == 0
