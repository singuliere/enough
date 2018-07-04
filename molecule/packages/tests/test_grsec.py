import testinfra

testinfra_hosts = ['trusty-host']

def try_if_letsencrypt(host):
    with host.sudo():
        return host.file("/etc/letsencrypt").exists

def test_grsec(host):
    trusty_host = host
    packages_host = testinfra.host.Host.get_host(
        'ansible://packages-host',
        ansible_inventory=host.backend.ansible_inventory)

    cmd = packages_host.run("""
    set -xe

    ln -sf /home/debian/linux-packages/opt /var/www/html/grsec
    cd /var/www/html/grsec
    dpkg-scanpackages . /dev/null | gzip > Packages.gz
    dpkg-scansources . /dev/null | gzip > Sources.gz
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc

    cmd = trusty_host.run("""
    set -xe

    sudo ifdown eth0 ; sudo ifup eth0 # setup resolv.conf
    echo 'Acquire::https {{ Verify-Peer "false"; Verify-Host "false"; }}' | sudo tee /etc/apt/apt.conf.d/01https
    sudo apt-get install -y dpkg-dev
    domain=$(hostname -d)
    (
      echo deb http{s}://packages.$domain/grsec ./
      echo deb-src http{s}://packages.$domain/grsec ./
    ) | sudo tee -a /etc/apt/sources.list
    sudo apt-get update
    sudo apt-get --allow-unauthenticated install -y linux-image-4.4.135-grsec
    sudo apt-get --allow-unauthenticated source linux-image-4.4.135-grsec
    """.format(s=('s' if try_if_letsencrypt(host) else '')))
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
