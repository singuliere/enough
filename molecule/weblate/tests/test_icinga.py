import urllib3
import re
import requests
import pytest
import yaml

testinfra_hosts = ['icinga_host']

def get_auth(host):
    with host.sudo():
        f = host.file("/etc/icinga2/conf.d/api-users.conf")
        return (
            re.search('ApiUser "(.*)"', f.content_string).group(1),
            re.search('password = "(.*)"', f.content_string).group(1)
        )
    
def get_master_address(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['icinga_host']['ansible_host']
    return address

def sloppy_get(url, headers={}, auth=None):
    s = requests.Session()
    s.auth = auth
    s.headers.update(headers)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    r = s.get(url, verify=False)
    r.raise_for_status()
    return r

def test_icinga_api_hosts(host):
    address = get_master_address(host)
    r = sloppy_get(
            'https://{address}:5665/v1/objects/hosts/weblate_host'.format(address=address),
            {'Accept': 'application/json'},
            get_auth(host),
            )
    answer = r.json()
    assert len(answer['results']) == 1
    assert answer['results'][0]['name'] == 'weblate_host'

def test_icinga_api_services (host):
    address = get_master_address(host)
    r = sloppy_get(
            'https://{address}:5665/v1/objects/services?host=weblate_host'.format(address=address),
            {'Accept': 'application/json'},
            get_auth(host),
            )
    answer = r.json()
    assert len(answer['results']) > 10
    assert len([s for s in answer['results'] if 'weblate_host!Weblate' == s['name']]) == 1
