import requests
import time


#
# Not using python-gitlab because it does not support /oauth/token
# see https://github.com/python-gitlab/python-gitlab/issues/753
#
#
# https://docs.gitlab.com/ce/api/oauth2.html#resource-owner-password-credentials
#
class GitLab(object):

    def __init__(self, url, username, password):
        self.url = url
        self.s = self._session(username, password)

    def _session(self, username, password):
        s = requests.Session()
        s.verify = '../../certs'
        r = s.post(self.url + '/oauth/token', json={
            'username': 'root',
            'password': password,
            'grant_type': 'password',
        })
        s.api = self.url + '/api/v4'
        r.raise_for_status()
        s.headers['Authorization'] = 'Bearer ' + r.json()['access_token']
        return s

    def get_namespace(self, user):
        r = self.s.get(self.s.api + '/namespaces?search=' + user)
        r.raise_for_status()
        return r.json()[0]['id']

    def recreate_project(self, user, project):
        namespace_id = self.get_namespace(user)
        r = self.s.get(self.s.api + '/projects/' + user + '%2F' + project)
        if r.status_code == requests.codes.ok:
            r = self.s.delete(self.s.api + '/projects/' + user + '%2F' + project)
            r.raise_for_status()
        for _ in range(10):
            r = self.s.post(self.s.api + '/projects', data={
                "name": project,
                "namespace_id": int(namespace_id),
                "visibility": "public",
            })
            time.sleep(5)
            if r.status_code == 201:
                break
            print(str(r.text))
        r.raise_for_status()

    def create_api_application(self, domain):
        callbacks = [
            f'https://api.{domain}/',
            f'https://api.{domain}/accounts/gitlab/',
            f'https://api.{domain}/accounts/gitlab/login/callback/',
        ]
        r = self.s.post(self.s.api + '/applications', json={
            'name': 'api',
            'redirect_uri': "\n".join(callbacks),
            'scopes': "api\nread_user",
            })
        r.raise_for_status()
        j = r.json()
        return j['application_id'], j['secret']
