import re
testinfra_hosts = ['website-host']


def check_priority(host, name, priority):
    cmd = host.run('apt-cache policy {}'.format(name))
    assert 0 == cmd.rc

    candidate = re.search(r'Candidate: ([^ ]+)\n', cmd.stdout).group(1)

    # Nota Bene: triple stars mean that the package is installed.
    # So de facto the test ensure that Installed == Candidate and
    # it might fails if there is a legitimate uninstalled update.
    # This should not occurs in a testing environment, but...
    assert ' *** {} {}'.format(candidate, priority) in cmd.stdout


def test_hugo(host):
    check_priority(host, 'hugo', 942)


def test_tasksel(host):
    check_priority(host, 'tasksel', 500)


def test_busted_buster(host):
    cmd = host.run('apt-cache policy')
    assert 0 == cmd.rc

    assert '-10 http://deb.debian.org/debian buster' in cmd.stdout
