import urllib3
import requests
import yaml

import gitlab_utils

testinfra_hosts = ['gitlab-host']


def get_variables():
    variables = yaml.load(open(
        '../../molecule/gitlab/roles/mirror/defaults/main.yml'))
    return variables


def test_mirror(host):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    (scheme, address) = gitlab_utils.get_address(host)
    url = scheme + '://' + address
    headers = {'Authorization': gitlab_utils.get_token(url)}
    variables = get_variables()
    api = url + '/api/v3'
    user = variables['mirror_bot_user']
    if not gitlab_utils.get_user(api, headers, user=user):
        gitlab_utils.create_user(api, headers,
                                 user=user,
                                 password=variables['mirror_bot_password'])
    gitlab_utils.recreate_test_project(
        api, headers, variables['mirror_bot_user'], 'securedrop')
    cmd = host.run("crontab -l | sed -e 's/.* \* \*//' | bash -xe")
    print(cmd.stdout)
    print(cmd.stderr)
    assert 0 == cmd.rc
    r = requests.get(
        scheme + '://' + address + '/' + user + '/securedrop/raw/master/LICENSE',
        headers=headers,
        verify='../../certs')
    r.raise_for_status()
    assert 'Affero General Public License' in r.text
