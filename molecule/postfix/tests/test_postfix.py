import time
import testinfra

testinfra_hosts = ['postfix-host']


def test_sendmail(host):
    domain = host.run("hostname -d").stdout.strip()

    postfix_host = host
    postfix_client_host = testinfra.host.Host.get_host(
        'ansible://icinga-host',
        ansible_inventory=host.backend.ansible_inventory)

    cmd = postfix_client_host.run("""
    ( echo 'To: loic+boundtofail@dachary.org' ; echo POSTFIX TEST ) |
    /usr/sbin/sendmail -v -F 'NO REPLY' -f 'noreply@{}' -t
    """.format(domain))
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc

    check = ("grep -q 'Untrusted TLS connection established to postfix-host' "
             "/var/log/syslog")
    for _ in range(300):
        print(check)
        cmd = postfix_client_host.run(check)
        if cmd.rc == 0:
            break
        time.sleep(1)

    check = ("grep -q 'connection established to spool.mail.gandi.net' "
             "/var/log/mail.log")
    for _ in range(300):
        print(check)
        cmd = postfix_host.run(check)
        if cmd.rc == 0:
            break
        time.sleep(1)
    assert 0 == postfix_host.run(check).rc
