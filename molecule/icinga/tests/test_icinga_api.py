import urllib3
import re
import requests
import pytest
import yaml

testinfra_hosts = ['icinga-host']

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_auth(host):
    host= host.get_host('ansible://icinga-host', ansible_inventory=host.backend.ansible_inventory)
    with host.sudo():
        f = host.file("/etc/icinga2/conf.d/api-users.conf")
        return (
            re.search('ApiUser "(.*)"', f.content_string).group(1),
            re.search('password = "(.*)"', f.content_string).group(1)
        )
    
def get_address():
    vars_dir = '../../inventory/group_vars/all'
    return 'icinga.' + yaml.load(
        open(vars_dir + '/domain.yml'))['domain']

def get_api_session(host):
    s = requests.Session()
    s.auth = get_auth(host)
    s.headers.update({'Accept': 'application/json'})
    s.verify = False
    s.timeout = 5
    return s

def test_icinga_api_hosts(host):
    address = get_address()
    r = get_api_session(host).get(
        'https://{address}:5665/v1/objects/hosts'.format(address=address)
    )
    r.raise_for_status()
    answer = r.json()
    assert len(answer['results']) == 4
    assert set([h['name'] for h in answer['results']]) == set(['bind-host', 'icinga-host', 'monitoring-client-host', 'monitoring-client2-host'])

def test_icinga_api_services(host):
    address = get_address()
    r = get_api_session(host).get(
            'https://{address}:5665/v1/objects/services'.format(address=address),
            )
    r.raise_for_status()
    answer = r.json()
    assert len(answer['results']) > 40
    assert host.backend.host != "monitoring-client-host" or len([s for s in answer['results'] if 'monitoring-client-host!Secure Drop Forum' == s['name']]) == 1
    assert len([s for s in answer['results'] if 'icinga-host!Manhack Securedrop instance over Tor' == s['name']]) == 1
