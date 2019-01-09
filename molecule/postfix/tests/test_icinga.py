from tests.icinga_helper import IcingaHelper

testinfra_hosts = ['icinga-host']


class TestChecks(IcingaHelper):

    def test_host(self):
        r = self.get_client().objects.get('Host', 'postfix-host')
        assert r['attrs']['name'] == 'postfix-host'

    def test_service(self, host):
        #  r = self.get_client().objects.list('Service', joins=['host.name'])
        with host.sudo():
            host.run("systemctl restart icinga2")
        assert self.is_service_ok('postfix-host!Check smtps TLS certificate')
