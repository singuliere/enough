testinfra_hosts = ['bind-host']

def test_certs(host):
    with host.sudo():
        host.run("apt-get install -y curl")
    # bind host does not know about the fake LE CA and cannot verify nginx-host
    assert host.run("! curl -m 5 -I https://nginx-host.$(hostname -d)").rc == 0
    assert host.run("curl -k -m 5 -I https://nginx-host.$(hostname -d)").rc == 0
    assert host.run("curl -m 5 -I https://bind-host.$(hostname -d)").rc == 0
