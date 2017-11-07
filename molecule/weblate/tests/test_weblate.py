import urllib3
import time
import requests
import pytest
import yaml

def get_weblate_address(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['weblate-host']['ansible_host']
    return address

def test_weblate (host):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # weblate freshly recreated may take few mins to be operationnal
    for i in range (60, 0, -1):
        try:
            s = requests.Session()
            r = s.get('http://{}'.format(get_weblate_address (host)), timeout=5)
            if r.status_code == requests.codes.ok:
                break
        except Exception as e:
            if i == 1:
                raise e
            time.sleep(5)
    assert 'Weblate' in r.text
