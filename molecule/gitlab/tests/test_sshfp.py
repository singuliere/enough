testinfra_hosts = ['bind-host']


def test_sshfp(host):
    domain = host.run('hostname -d').stdout.strip()
    #
    # expected side effect of
    #
    #     - role: install_ssh_records
    #       vars:
    #         install_ssh_records_host: lab
    #
    cmd = host.run('dig sshfp +noall +answer @ns1.{domain} lab.{domain}'.format(
        domain=domain))
    assert cmd.rc == 0
    assert 'IN SSHFP' in cmd.stdout
    assert 'lab.' + domain in cmd.stdout
