from pprint import pprint
import testinfra
import requests
import yaml
from enough.common import retry

testinfra_hosts = ['wazuh-host']


class Wazuh(object):

    def __init__(self):
        self.url = 'http://{}:55000'.format(self.get_address())
        self.s = requests.session()
        self.s.auth = ('frob', 'nitz')
        self.s.headers = {
            'Accept': 'application/json',
        }

    def get_address(self):
        vars_dir = '../../inventory/group_vars/all'
        return 'wazuh.' + yaml.load(
            open(vars_dir + '/domain.yml'))['domain']

    def get_check_times(self, type):
        r = self.s.get(self.url + '/' + type + '/001/last_scan')
        r.raise_for_status()
        d = r.json()
        assert d['error'] == 0
        return (d['data']['start'], d['data']['end'])

    @retry.retry(AssertionError, tries=8)
    def wait_for_checks(self):
        # start time > end time means the check is ongoing
        for type in ('syscheck', 'rootcheck'):
            (start, end) = self.get_check_times(type)
            assert start < end

    def get_syscheck_end(self):
        return self.get_check_times('syscheck')[1]

    def run_syscheck(self):
        last = self.get_syscheck_end()
        r = self.s.put(self.url + '/syscheck/001')
        r.raise_for_status()
        d = r.json()
        pprint(d)
        assert d['error'] == 0

        @retry.retry(AssertionError, tries=8)
        def wait_for_syscheck():
            assert self.get_syscheck_end() > last
        wait_for_syscheck()

    def get_syscheck_md5(self, path):
        r = self.s.get(self.url + '/syscheck/001?file=' + path)
        r.raise_for_status()
        d = r.json()
        assert d['error'] == 0
        info = d['data']['items'][0]
        assert info['file'] == path
        return info['md5']


def test_wazuh(host):
    # postfix_host is a wazuh agent
    postfix_host = testinfra.host.Host.get_host(
        'ansible://postfix-host',
        ansible_inventory=host.backend.ansible_inventory)

    #
    # it can fail sometimes because of https://github.com/wazuh/wazuh/issues/2236
    #
    postfix_host
    w = Wazuh()
    w.run_syscheck()
    good_md5 = w.get_syscheck_md5('/etc/fuse.conf')
    # tamper with a file on the postfix-host
    with postfix_host.sudo():
        postfix_host.run("""
        echo HACK >> /etc/fuse.conf
        """)
    w.run_syscheck()
    bad_md5 = w.get_syscheck_md5('/etc/fuse.conf')
    assert good_md5 != bad_md5
