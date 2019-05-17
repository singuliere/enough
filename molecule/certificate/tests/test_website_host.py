testinfra_hosts = ['website-host']


def test_can_curl_locally(host):
    with host.sudo():
        host.run("apt-get install -y curl")
    assert host.run("curl -m 5 -I https://website-host.$(hostname -d)").rc == 0
    assert host.run("grep 'SOMETHING TESTS CAN GREP' /etc/nginx/sites-enabled/*.conf").rc == 0


def test_bind_fails_because_no_lestencrypt_staging_ca_installed(host):
    bind_host = host.get_host('ansible://bind-host',
                              ansible_inventory=host.backend.ansible_inventory)
    with bind_host.sudo():
        bind_host.run("apt-get install -y curl")
    assert bind_host.run("curl -m 5 -I -k https://website-host.$(hostname -d)").rc == 0
    assert bind_host.run("curl -m 5 -I https://website-host.$(hostname -d)").rc == 60


def test_runner_succeeds_because_lestencrypt_staging_ca_installed(host):
    runner_host = host.get_host('ansible://runner-host',
                                ansible_inventory=host.backend.ansible_inventory)
    with runner_host.sudo():
        runner_host.run("apt-get install -y curl")
    assert runner_host.run("curl -m 5 -I https://website-host.$(hostname -d)").rc == 0
