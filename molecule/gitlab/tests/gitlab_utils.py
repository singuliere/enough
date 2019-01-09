import requests
import time
import yaml


def get_address(host):
    vars_dir = '../../inventories/common/group_vars/all'
    return ('https', 'lab.' + yaml.load(
        open(vars_dir + '/domain.yml'))['domain'])


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


def get_namespace(url, headers, user):
    r = requests.get(url + '/namespaces?search=' + user,
                     headers=headers,
                     verify='../../certs')
    r.raise_for_status()
    return r.json()[0]['id']


def recreate_test_project(url, headers, user, project):
    namespace_id = get_namespace(url, headers, user)
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
