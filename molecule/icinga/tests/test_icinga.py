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
    
def test_icinga_api_hosts(File, host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts'][host.backend.host]['ansible_host']
    s = requests.Session()
    s.auth = get_auth(File)
    s.headers.update({'Accept': 'application/json'})
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    r = s.get('https://{address}:5665/v1/objects/hosts'.format(
        address=address,
    ), verify=False)
    r.raise_for_status()
    answer = r.json()
    assert len(answer['results']) == 1
    assert answer['results'][0]['name'] == 'icinga_host'

def test_icinga_api_services (File, host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts'][host.backend.host]['ansible_host']
    s = requests.Session()
    s.auth = get_auth(File)
    s.headers.update({'Accept': 'application/json'})
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    r = s.get('https://{address}:5665/v1/objects/services'.format(
        address=address,
    ), verify=False)
    r.raise_for_status()
    answer = r.json()
    assert len(answer['results']) > 10

def test_icingaweb2_login_screen(File, host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts'][host.backend.host]['ansible_host']
    s = requests.Session()
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    r = s.get('http://{address}/icingaweb2/authentication/login'.format(
        address=address,
    ), verify=False)
    cookies= dict(r.cookies)
    r = s.get('http://{address}/icingaweb2/authentication/login?_checkCookie=1'.format(
        address=address,
    ), cookies=cookies, verify=False)
    r.raise_for_status()
    assert 'Icinga Web 2 Login' in r.text
