testinfra_hosts = ['bind-host']


def test_can_curl_locally(host):
    with host.sudo():
        host.run("apt-get install -y curl")
    assert host.run("curl -m 5 -I https://bind-host.$(hostname -d)").rc == 0


def test_cloud_can_curl(host):
    cloud_host = host.get_host('ansible://cloud-host',
                               ansible_inventory=host.backend.ansible_inventory)
    with cloud_host.sudo():
        cloud_host.run("apt-get install -y cloud")
    assert cloud_host.run("curl -m 5 -I https://bind-host.$(hostname -d)").rc == 0
