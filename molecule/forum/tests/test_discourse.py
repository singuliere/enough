testinfra_hosts = ['forum-host']

def test_discourse(host):
    cmd = host.run("""
    set -xe
    curl --silent https://forum.$(hostname -d) | grep --quiet 'Congratulations, you installed Discourse!'
    """)
    assert 0 == cmd.rc
