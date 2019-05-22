from tests.icinga_helper import IcingaHelper

testinfra_hosts = ['icinga-host']


class TestChecks(IcingaHelper):

    def test_icinga_host(self):
        r = self.get_client().objects.get('Host', 'bind-host')
        assert r['attrs']['name'] == 'bind-host'

    def test_icinga_service(self, host):
        #  r = self.get_client().objects.list('Service', joins=['host.name'])
        with host.sudo():
            host.run("systemctl restart icinga2")
        assert self.is_service_ok('bind-host!ping4')
        domain = host.run("hostname -d").stdout.strip()
        assert self.is_service_ok('bind-host!Zone test.' + domain)
        assert self.is_service_ok('bind-host!Zone ' + domain)
