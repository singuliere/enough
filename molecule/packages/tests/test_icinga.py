from tests.icinga_helper import IcingaHelper

testinfra_hosts = ['icinga-host']


class TestChecks(IcingaHelper):

    def test_host(self):
        r = self.get_client().objects.get('Host', 'packages-host')
        assert r['attrs']['name'] == 'packages-host'

    def test_service(self, host):
        assert self.is_service_ok('packages-host!Packages')
