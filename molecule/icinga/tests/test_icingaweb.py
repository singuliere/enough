import urllib3
import re
import requests
import pytest
import yaml

testinfra_hosts = ['icinga-host']

def get_master_address(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['icinga-host']['ansible_host']
    return address

def get_master_fqdn(host):
    host= host.get_host('ansible://icinga-host', ansible_inventory=host.backend.ansible_inventory)
    with host.sudo():
        f = host.file("/etc/nginx/sites-enabled/icinga-host")
        return re.search('server_name (.*);', f.content_string).group(1)

def try_if_letsencrypt(host):
    host= host.get_host('ansible://icinga-host', ansible_inventory=host.backend.ansible_inventory)
    with host.sudo():
        return host.file("/etc/letsencrypt").exists

def test_icingaweb2_login_screen(host):
    if try_if_letsencrypt(host):
        proto_srv= "https://{address}".format(address=get_master_fqdn(host))
    else:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        proto_srv= "http://{address}".format(address=get_master_address(host))
    s = requests.Session()
    s.verify = '../../certs'
    r = s.get(proto_srv+'/icingaweb2/authentication/login', timeout=5)
    cookies= dict(r.cookies)
    r = s.get(proto_srv+'/icingaweb2/authentication/login?_checkCookie=1', cookies=cookies, timeout=5)
    r.raise_for_status()
    assert 'Icinga Web 2 Login' in r.text
