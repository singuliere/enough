import urllib3
import re
import requests
import pytest
import yaml

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
    if not try_if_letsencrypt(host):
        return True

    address = get_master_fqdn(host)
    print ('https://{address}/icingaweb2/authentication/login'.format(address=address))
    s = requests.Session()
    r = s.get('https://{address}/icingaweb2/authentication/login'.format(
        address=address,
    ))
    cookies= dict(r.cookies)
    r = s.get('https://{address}/icingaweb2/authentication/login?_checkCookie=1'.format(
        address=address,
    ), cookies=cookies)
    r.raise_for_status()
    assert 'Icinga Web 2 Login' in r.text