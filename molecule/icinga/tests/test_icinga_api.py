import urllib3

from tests.icinga_helper import IcingaHelper

testinfra_hosts = ['icinga-host']

class TestApi(IcingaHelper):

    def test_icinga_api_hosts(self, host):
        address = self.get_address()
        r = self.get_api_session(host).get(
            'https://{address}:5665/v1/objects/hosts'.format(address=address)
        )
        r.raise_for_status()
        answer = r.json()
        assert len(answer['results']) == 4
        assert set([h['name'] for h in answer['results']]) == set(['bind-host', 'icinga-host', 'monitoring-client-host', 'monitoring-client2-host'])

    def test_icinga_api_services(self, host):
        address = self.get_address()
        r = self.get_api_session(host).get(
                'https://{address}:5665/v1/objects/services'.format(address=address),
                )
        r.raise_for_status()
        answer = r.json()
        assert len(answer['results']) > 40
        assert host.backend.host != "monitoring-client-host" or len([s for s in answer['results'] if 'monitoring-client-host!Secure Drop Forum' == s['name']]) == 1
        assert len([s for s in answer['results'] if 'icinga-host!Manhack Securedrop instance over Tor' == s['name']]) == 1

    def test_icinga_ntp_time(self, host):
        assert self.is_service_ok(host, 'monitoring-client-host!systemd-timesyncd is working')
