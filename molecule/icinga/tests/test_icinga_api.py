import urllib3
import re
import requests
import pytest
import yaml

import retry

testinfra_hosts = ['icinga-host']

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TestApi(object):

    def get_auth(self, host):
        host= host.get_host('ansible://icinga-host', ansible_inventory=host.backend.ansible_inventory)
        with host.sudo():
            f = host.file("/etc/icinga2/conf.d/api-users.conf")
            return (
                re.search('ApiUser "(.*)"', f.content_string).group(1),
                re.search('password = "(.*)"', f.content_string).group(1)
            )

    def get_address(self):
        vars_dir = '../../inventory/group_vars/all'
        return 'icinga.' + yaml.load(
            open(vars_dir + '/domain.yml'))['domain']

    def get_api_session(self, host):
        s = requests.Session()
        s.auth = self.get_auth(host)
        s.headers.update({'Accept': 'application/json'})
        s.verify = False
        s.timeout = 5
        return s

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

    @retry.retry(AssertionError, tries=7)
    def wait_for_service(self, session, api, name):
        r = session.get(
            '{api}/objects/services/{name}'.format(api=api, name=name)
        )
        r.raise_for_status()
        answer = r.json()
        assert int(answer['results'][0]['attrs']['state']) == 0
        return True

    def is_service_ok(self, host, name):
        #
        # force the check to reduce the waiting time
        #
        session = self.get_api_session(host)
        api = 'https://{}:5665/v1'.format(self.get_address())
        r = session.post(
            '{api}/actions/reschedule-check'.format(api=api),
            json={
                "type": "Service",
                "filter": "service.__name==\"{}\"".format(name),
                "force": True,
            }
        )
        r.raise_for_status()
        answer = r.json()
        assert len(answer['results']) == 1
        assert int(answer['results'][0]['code']) == 200

        return self.wait_for_service(session, api, name)

    def test_icinga_ntp_time(self, host):
        assert self.is_service_ok(host, 'monitoring-client-host!systemd-timesyncd is working')
