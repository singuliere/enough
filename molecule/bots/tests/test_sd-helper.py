testinfra_hosts = ['bots-host']

def test_sd_helper(host):
    cmd = host.run("""
    cd /srv/sd-helper
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
