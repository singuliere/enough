import urllib3
import re
import requests
import pytest
import yaml

def get_master_address(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['icinga_host']['ansible_host']
    return address

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
