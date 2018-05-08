import re
testinfra_hosts = ['website-host']

def check_priority (host, name, priority):
    cmd = host.run('apt-cache policy {}'.format(name))
    assert 0 == cmd.rc

    candidate= re.search(r'Candidate: ([^ ]+)\n', cmd.stdout).group(1)

    assert ' *** {} {}'.format(candidate, priority) in cmd.stdout

def test_hugo (host):
    check_priority (host, 'hugo', 942)

def test_tasksel (host):
    check_priority (host, 'tasksel', 500)

def test_busted_buster (host):
    cmd = host.run('apt-cache policy')
    assert 0 == cmd.rc

    assert '-10 http://deb.debian.org/debian buster' in cmd.stdout
