testinfra_hosts = ['chat-host']

def test_mattermost(host):
    cmd = host.run("""
    exit 0
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
