import time
import requests
import yaml


def get_address():
    vars_dir = '../../inventory/group_vars/all'
    return 'https://weblate.' + yaml.load(
        open(vars_dir + '/domain.yml'))['domain']


def test_weblate():
    # weblate freshly recreated may take few mins to be operationnal
    url = get_address()
    for i in range(60, 0, -1):
        r = requests.get(url, timeout=5, verify='../../certs')
        if r.status_code == requests.codes.ok:
            break
        time.sleep(5)
    assert 'Weblate' in r.text
