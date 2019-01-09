import requests
import yaml

testinfra_hosts = ['icinga-host']


def get_address():
    vars_dir = '../../inventories/common/group_vars/all'
    return 'icinga.' + yaml.load(
        open(vars_dir + '/domain.yml'))['domain']


def test_icingaweb2_login_screen(host):
    proto_srv = "https://{address}".format(address=get_address())
    s = requests.Session()
    s.verify = '../../certs'
    r = s.get(proto_srv+'/icingaweb2/authentication/login', timeout=5)
    cookies = dict(r.cookies)
    r = s.get(proto_srv+'/icingaweb2/authentication/login?_checkCookie=1',
              cookies=cookies, timeout=5)
    r.raise_for_status()
    assert 'Icinga Web 2 Login' in r.text
