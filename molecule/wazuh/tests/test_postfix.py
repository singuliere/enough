import testinfra
from enough.common import retry

testinfra_hosts = ['wazuh-host']


def test_wazuh_send_mail(host):

    wazuh_host = host
    postfix_host = testinfra.host.Host.get_host(
        'ansible://postfix-host',
        ansible_inventory=host.backend.ansible_inventory)

    with wazuh_host.sudo():
        def wait_for_boot_mail():
            assert wazuh_host.run("""
            grep -q -r 'ossec: Ossec started.' /var/spool/postfix/deferred
            """).rc == 0
        wait_for_boot_mail()

    check = ("grep -q 'proto=ESMTP helo=<wazuh-host' "
             "/var/log/mail.log")

    @retry.retry(AssertionError, tries=8)
    def wait_for_mail():
        assert postfix_host.run(check).rc == 0
    wait_for_mail()
