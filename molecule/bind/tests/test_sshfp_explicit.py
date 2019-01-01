testinfra_hosts = [ 'bind-host' ]

def test_sshfp(host):
    domain = host.run('hostname -d').stdout.strip()
    #
    # expected side effect of
    #
    #     - role: install_ssh_records
    #       vars:
    #         install_ssh_records_host: ns1
    #
    with host.sudo():
        assert host.file('/var/cache/bind/' + domain).contains('ns1 IN SSHFP')
