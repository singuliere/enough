import re

testinfra_hosts = ['packages-host']

def test_packages(host):
    cmd = host.run("""
    set -xe

    ! test -f /var/log/update-packages.log.1.gz
    sudo /usr/sbin/logrotate --force /etc/logrotate.d/packages-logrotate
    test -f /var/log/update-packages.log.1.gz
    test debian = $(stat --format=%U /var/log/update-packages.log)
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc

def test_displayed_packages(host):
    webpage= host.run("""
    domain=$(hostname -d)
    curl -s -m 5 http{s}://packages.$domain
    """.format(s=('s' if try_if_letsencrypt(host) else ''))
    assert 0 == webpage.rc

    for url in re.findall(r'https?://[^\s"><]+', webpage.stdout):
        print(url)
        cmd= host.run("curl -s -I -m 5 {}")
        assert 'HTTP/2 200' in cmd.stdout or 'HTTP/2 301' in cmd.stdout
