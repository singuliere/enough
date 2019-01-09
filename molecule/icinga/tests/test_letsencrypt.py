import requests
import yaml

testinfra_hosts = ['icinga-host']


def get_address():
    vars_dir = '../../inventories/common/group_vars/all'
    return 'icinga.' + yaml.load(
        open(vars_dir + '/domain.yml'))['domain']


def test_icingaweb2_login_screen(host):
    address = get_address()
    print ('https://{address}/icingaweb2/authentication/login'.format(address=address))
    s = requests.Session()
    r = s.get('http://{address}/icingaweb2/authentication/login'.format(
        address=address,
    ), timeout=5)
    r.status_code = 302
    s.verify = '../../certs'
    r = s.get('https://{address}/icingaweb2/authentication/login'.format(
        address=address,
    ), timeout=5)
    cookies = dict(r.cookies)
    r = s.get('https://{address}/icingaweb2/authentication/login?_checkCookie=1'.format(
        address=address,
    ), cookies=cookies, timeout=5)
    r.raise_for_status()
    assert 'Icinga Web 2 Login' in r.text
