import time
import testinfra

testinfra_hosts = ['weblate-host']


def test_weblate_send_mail(host):

    weblate_host = host
    postfix_host = testinfra.host.Host.get_host(
        'ansible://postfix-host',
        ansible_inventory=host.backend.ansible_inventory)

    cmd = weblate_host.run("""
    cd /srv/weblate
    sudo docker-compose -f docker-compose-infrastructure.yml exec -T weblate weblate \
         sendtestemail loic+doomtofail@dachary.org
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
