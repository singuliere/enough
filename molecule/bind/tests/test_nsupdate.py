testinfra_hosts = ['bind-host']


def test_nsupdate_ssh_keys(host):
    with host.sudo():
        # X6yEpyb0O1DoPISER4tgxIb is
        # authorized_keys/roles/authorized_keys/files/nsupdate/singuliere.pub
        assert host.file('/home/subdomain/.ssh/authorized_keys').contains('X6yEpyb0O1DoPISER4tgxIb')
