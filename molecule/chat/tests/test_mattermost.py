testinfra_hosts = ['chat-host']

def test_mattermost(host):
    with host.sudo():
        host.run("apt-get install -y curl")

    assert host.run("curl -s -m 5 https://chat.$(hostname -d)").rc == 0
