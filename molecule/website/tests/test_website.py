testinfra_hosts = ['website-host']

def test_website(host):
    cmd = host.run("""
    set -xe
    flock /tmp/update-website \
          bash -x /srv/update-website.sh \
          >> /var/log/update-website.log 2>&1
    grep --quiet -i enough /usr/share/nginx/html/index.html
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc

    cmd = host.run("""
    set -xe

    ! test -f /var/log/update-website.log.1.gz
    sudo /usr/sbin/logrotate --force /etc/logrotate.d/website-logrotate
    test -f /var/log/update-website.log.1.gz
    test debian = $(stat --format=%U /var/log/update-website.log)
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc

    with host.sudo():
        host.run("apt-get install -y curl")

    assert host.run("curl -m 5 -I https://$(hostname -d)").rc == 0
    assert host.run("curl -m 5 -I https://www.$(hostname -d)").rc == 0
