import urllib3
import re
import requests
import pytest
import yaml

def get_auth(host):
    host= host.get_host('ansible://icinga-host', ansible_inventory=host.backend.ansible_inventory)
    with host.sudo():
        f = host.file("/etc/icinga2/conf.d/api-users.conf")
        return (
            re.search('ApiUser "(.*)"', f.content_string).group(1),
            re.search('password = "(.*)"', f.content_string).group(1)
        )
    
def get_master_address(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['icinga-host']['ansible_host']
    return address

def sloppy_get(url, headers={}, auth=None):
    s = requests.Session()
    s.auth = auth
    s.headers.update(headers)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    r = s.get(url, verify=False, timeout=5)
    r.raise_for_status()
    return r

def test_icinga_api_hosts(host):
    address = get_master_address(host)
    r = sloppy_get(
            'https://{address}:5665/v1/objects/hosts'.format(address=address,),
            {'Accept': 'application/json'},
            get_auth(host),
            )
    answer = r.json()
    assert len(answer['results']) == 3
    assert set([h['name'] for h in answer['results']]) == set(['icinga-host', 'monitoring-client-host', 'monitoring-client2-host'])

def test_icinga_api_services (host):
    address = get_master_address(host)
    r = sloppy_get(
            'https://{address}:5665/v1/objects/services'.format(address=address,),
            {'Accept': 'application/json'},
            get_auth(host),
            )
    answer = r.json()
    assert len(answer['results']) > 40
