from tests.icinga_helper import IcingaHelper

testinfra_hosts = ['icinga-host']


class TestChecks(IcingaHelper):

    def test_host(self):
        r = self.get_client().objects.get('Host', 'wereport-host')
        assert r['attrs']['name'] == 'wereport-host'

    def test_service(self, host):
        assert self.is_service_ok('wereport-host!wereport-host')
        assert self.is_service_ok('wereport-host!wereport-host over Tor')
