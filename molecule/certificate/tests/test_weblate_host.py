testinfra_hosts = ['weblate-host']


def test_can_curl_locally(host):
    with host.sudo():
        host.run("apt-get install -y curl")
    assert host.run("curl -m 5 -I https://weblate-host.$(hostname -d)").rc == 0


def test_file_behind_the_reverse_proxy_is_read(host):
    r = host.run("curl -s -m 5 https://weblate-host.$(hostname -d)/index.html")
    assert r.rc == 0
    assert 'SOMETHING' in r.stdout


def test_bind_fails_because_no_lestencrypt_staging_ca_installed(host):
    bind_host = host.get_host('ansible://bind-host',
                              ansible_inventory=host.backend.ansible_inventory)
    with bind_host.sudo():
        bind_host.run("apt-get install -y curl")
    assert bind_host.run("curl -m 5 -I -k https://weblate-host.$(hostname -d)").rc == 0
    assert bind_host.run("curl -m 5 -I https://weblate-host.$(hostname -d)").rc == 60


def test_runner_succeeds_because_lestencrypt_staging_ca_installed(host):
    runner_host = host.get_host('ansible://runner-host',
                                ansible_inventory=host.backend.ansible_inventory)
    with runner_host.sudo():
        runner_host.run("apt-get install -y curl")
    assert runner_host.run("curl -m 5 -I https://weblate-host.$(hostname -d)").rc == 0
