import urllib3
import re
import requests
import pytest
import yaml

def get_weblate_address(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['weblate-host']['ansible_host']
    return address

def test_weblate (host):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    s = requests.Session()
    print('http://{}'.format(get_weblate_address (host)))
    r = s.get('http://{}'.format(get_weblate_address (host)), timeout=5)
    r.raise_for_status()
    assert 'Weblate' in r.text
