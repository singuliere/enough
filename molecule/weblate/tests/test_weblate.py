import pytest
import time
import testinfra

testinfra_hosts = ['weblate_host']

def test_weblate(host):

    weblate_host = host
    postfix_host = testinfra.host.Host.get_host(
        'ansible://postfix_host',
        ansible_inventory=host.backend.ansible_inventory)

    cmd = weblate_host.run("""
    cd /srv/weblate
    sudo docker-compose exec -T weblate weblate sendtestemail loic@dachary.org
    """)
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc

    check = ("grep -q 'connection established to spool.mail.gandi.net' "
             "/var/log/mail.log")
    for _ in range(300):
        print(check)
        cmd = postfix_host.run(check)
        if cmd.rc == 0:
            break
        time.sleep(1)
    assert 0 == postfix_host.run(check).rc