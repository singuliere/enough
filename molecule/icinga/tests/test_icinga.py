import urllib3
import re
import requests
import pytest
import yaml

def get_auth(File):
    f = File("/srv/icinga2/icinga/etc/icinga2/conf.d/api-users.conf")
    return (
        re.search('ApiUser "(.*)"', f.content_string).group(1),
        re.search('password = "(.*)"', f.content_string).group(1)
    )
    
def get_master_address(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts'][host.backend.host]['ansible_host']
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
            'https://{address}:5665/v1/objects/hosts'.format(address=address,),
            {'Accept': 'application/json'},
            get_auth(host.file),
            )
    answer = r.json()
    assert len(answer['results']) == 1
    assert answer['results'][0]['name'] == 'icinga_host'

def test_icinga_api_services (host):
    address = get_master_address(host)
    r = sloppy_get(
            'https://{address}:5665/v1/objects/services'.format(address=address,),
            {'Accept': 'application/json'},
            get_auth(host.file),
            )
    answer = r.json()
    assert len(answer['results']) > 10

def test_icingaweb2_login_screen(host):
    address = get_master_address(host)
    s = requests.Session()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    r = s.get('http://{address}/icingaweb2/authentication/login'.format(
        address=address,
    ))
    cookies= dict(r.cookies)
    r = s.get('http://{address}/icingaweb2/authentication/login?_checkCookie=1'.format(
        address=address,
    ), cookies=cookies)
    r.raise_for_status()
    assert 'Icinga Web 2 Login' in r.text
