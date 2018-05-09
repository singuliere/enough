import testinfra

testinfra_hosts = ['trusty-host']

def try_if_letsencrypt(host):
    with host.sudo():
        return host.file("/etc/letsencrypt").exists

def test_securedrop(host):
    trusty_host = host
    packages_host = testinfra.host.Host.get_host(
        'ansible://packages-host',
        ansible_inventory=host.backend.ansible_inventory)

    cmd = packages_host.run("""
    set -xe
    flock /tmp/update-packages \
          bash -x /srv/securedrop-update-packages.sh 0.6 \
          >> /var/log/update-packages.log 2>&1
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc

    cmd = trusty_host.run("""
    set -xe

    sudo ifdown eth0 ; sudo ifup eth0 # setup resolv.conf
    echo 'Acquire::https { Verify-Peer "false"; Verify-Host "false"; }' > /etc/apt/apt.conf.d/01https
    sudo apt-get install dpkg-dev
    domain=$(hostname -d)
    sudo apt-add-repository --enable-source http{s}://packages.$domain/0.6
    wget http{s}://packages.$domain/key.asc
    sudo apt-key add key.asc
    sudo apt-get source linux-image-4.4.115-grsec
    sudo apt-get install -y securedrop-ossec-agent
    """.format(s=('s' if try_if_letsencrypt(host) else '')))
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
