testinfra_hosts = ['website-host']


def test_nginx(host):
    with host.sudo():
        host.run("apt-get install -y curl")
    assert host.run("curl -m 5 -I http://website-host.$(hostname -d)").rc == 0
    assert host.run("grep 'SOMETHING TESTS CAN GREP' /etc/nginx/sites-enabled/*.conf").rc == 0
