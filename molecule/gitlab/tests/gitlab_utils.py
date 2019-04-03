import requests
import time
import yaml


def get_fqdn(host):
    vars_dir = '../../inventories/common/group_vars/all'
    return 'lab.' + yaml.load(open(vars_dir + '/domain.yml'))['domain']


def get_url(host):
    return 'https://' + get_fqdn(host)


def get_password():
    variables = yaml.load(open(
        '../../molecule/gitlab/roles/gitlab/defaults/main.yml'))
    return variables['gitlab_password']


#
# Not using python-gitlab because it does not support /oauth/token
# see https://github.com/python-gitlab/python-gitlab/issues/753
#
#
# https://docs.gitlab.com/ce/api/oauth2.html#resource-owner-password-credentials
#
def session(host):
    s = requests.Session()
    s.verify = '../../certs'
    url = get_url(host)
    r = s.post(url + '/oauth/token', json={
        'username': 'root',
        'password': get_password(),
        'grant_type': 'password',
    })
    s.api = url + '/api/v4'
    r.raise_for_status()
    s.headers['Authorization'] = 'Bearer ' + r.json()['access_token']
    return s


def get_namespace(session, user):
    r = session.get(session.api + '/namespaces?search=' + user)
    r.raise_for_status()
    return r.json()[0]['id']


def recreate_test_project(session, user, project):
    namespace_id = get_namespace(session, user)
    r = session.get(session.api + '/projects/' + user + '%2F' + project)
    if r.status_code == requests.codes.ok:
        r = session.delete(session.api + '/projects/' + user + '%2F' + project)
        r.raise_for_status()
    for _ in range(10):
        r = session.post(session.api + '/projects', data={
            "name": project,
            "namespace_id": int(namespace_id),
            "visibility": "public",
        })
        time.sleep(5)
        if r.status_code == 201:
            break
        print(str(r.text))
    r.raise_for_status()
