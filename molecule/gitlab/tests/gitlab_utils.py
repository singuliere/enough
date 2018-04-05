import os
import requests
import time
import yaml


def get_address(host):
    for vars_dir in ('group_vars/all', '../../inventory/group_vars/all'):
        with_https_path = vars_dir + '/with_https.yml'
        if os.path.exists(with_https_path):
            with_https = yaml.load(open(with_https_path))
            if with_https and with_https.get('with_https'):
                return ('https', 'lab.' + yaml.load(
                    open(vars_dir + '/domain.yml'))['domain'])
    inventory = yaml.load(open(host.backend.ansible_inventory))
    return ('http', inventory['all']['hosts']['gitlab-host']['ansible_host'])


def get_password():
    variables = yaml.load(open(
        '../../molecule/gitlab/roles/gitlab/defaults/main.yml'))
    return variables['gitlab_password']

#
# https://docs.gitlab.com/ce/api/oauth2.html#resource-owner-password-credentials
#
def get_token(url):
    r = requests.post(url + '/oauth/token', json={
        'username': 'root',
        'password': get_password(),
        'grant_type': 'password',
    }, verify='../../certs')
    r.raise_for_status()
    return 'Bearer ' + r.json()['access_token']


def get_user(url, headers, user):
    r = requests.get(url + '/users?username=' + user,
                     headers=headers,
                     verify='../../certs')
    return len(r.json()) > 0


def create_user(url, headers, user, password):
    r = requests.post(url + '/users', headers=headers, data={
        "email": "info@example.com",
        "username": user,
        "name": user,
        "password": password,
    }, verify='../../certs')
    r.raise_for_status()


def get_or_create_namespace(url, headers, user):
    r = requests.get(url + '/namespaces?search=' + user,
                     headers=headers,
                     verify='../../certs')
    r.raise_for_status()
    return r.json()[0]['id']


def recreate_test_project(url, headers, user, project):
    namespace_id = get_or_create_namespace(url, headers, user)
    r = requests.get(url + '/projects/' + user + '%2F' + project,
                     headers=headers,
                     verify='../../certs')
    if r.status_code == requests.codes.ok:
        r = requests.delete(url + '/projects/' + user + '%2F' + project,
                            headers=headers,
                            verify='../../certs')
        r.raise_for_status()
    for _ in range(10):
        r = requests.post(url + '/projects', headers=headers, data={
            "name": project,
            "namespace_id": int(namespace_id),
            "visibility": "public",
        }, verify='../../certs')
        time.sleep(5)
        if r.status_code == 201:
            break
        print(str(r.text))
    r.raise_for_status()
