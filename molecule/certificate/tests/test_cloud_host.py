testinfra_hosts = ['cloud-host']


def test_can_curl_locally(host):
    with host.sudo():
        host.run("apt-get install -y curl")
    assert host.run("curl -m 5 -I https://cloud-host.$(hostname -d)").rc == 0
    assert host.run("grep 'SOMETHING TESTS CAN GREP' /etc/nginx/sites-enabled/*.conf").rc == 0


def test_website_fails_because_no_ownca_installed(host):
    website_host = host.get_host('ansible://website-host',
                                 ansible_inventory=host.backend.ansible_inventory)
    with website_host.sudo():
        website_host.run("apt-get install -y curl")
    assert website_host.run("curl -m 5 -I -k https://cloud-host.$(hostname -d)").rc == 0
    assert website_host.run("curl -m 5 -I https://cloud-host.$(hostname -d)").rc == 60


def test_runner_succeeds_because_ownca_installed(host):
    runner_host = host.get_host('ansible://runner-host',
                                ansible_inventory=host.backend.ansible_inventory)
    with runner_host.sudo():
        runner_host.run("apt-get install -y curl")
    assert runner_host.run("curl -m 5 -I https://cloud-host.$(hostname -d)").rc == 0
