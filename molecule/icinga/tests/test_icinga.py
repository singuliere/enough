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
    
def test_icinga(File, host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts'][host.backend.host]['ansible_host']
    s = requests.Session()
    s.auth = get_auth(File)
    s.headers.update({'Accept': 'application/json'})
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    r = s.get('https://{address}:5665/v1/objects/services?service=icinga2!ping4&attrs=host_name&attrs=state'.format(
        address=address,
    ), verify=False)
    r.raise_for_status()
    service = r.json()
    assert 0 == service['state']
