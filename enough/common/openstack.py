from bs4 import BeautifulSoup
import copy
import hashlib
import os
import requests
import sh
import yaml


class Heat(object):

    def __init__(self, config_file):
        self.h = sh.openstack.bake('--os-cloud=ovh', _env={
            'OS_CLIENT_CONFIG_FILE': config_file,
        })

    @staticmethod
    def get_stack_definitions():
        path = os.path.join(os.path.dirname(__file__), 'data/stacks.yaml')
        return yaml.load(open(path))['stacks']

    @staticmethod
    def get_stack_definition(host):
        definition = {
            'name': host,
        }
        definition.update(Heat.get_stack_definitions()[host])
        return definition

    def is_working(self):
        # retry to verify the API is stable
        for _ in range(5):
            try:
                self.h.stack.list()
            except sh.ErrorReturnCode_1:
                return False
        return True


class OpenStack(object):

    def __init__(self, config_file):
        self.config = yaml.load(open(config_file))
        self.auth = self.config['clouds']['ovh']['auth']
        self.horizon_session = None

    def login_horizon(self):
        url = 'https://horizon.cloud.ovh.net'

        if self.horizon_session is None:
            s = requests.Session()

            r = s.get(url)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            #  print(soup.prettify())
            data = {}
            for input in soup.select('form[action="/auth/login/"] input'):
                if input.get('name') is None or input.get('value') is None:
                    continue
                data[input['name']] = input['value']
            data['username'] = data['fake_email'] = self.auth['username']
            data['password'] = data['fake_password'] = self.auth['password']

            r = s.post(url + '/auth/login/', data=data, allow_redirects=False)
            r.raise_for_status()
            assert r.status_code == 302
            assert r.headers['Location'] == url + '/'

            r = s.get(r.headers['Location'], allow_redirects=False)
            r.raise_for_status()
            assert r.status_code == 302
            assert r.headers['Location'] == url + '/project/'

            self.horizon_session = s

        return url, self.horizon_session

    def region_list(self):
        (url, s) = self.login_horizon()
        r = s.get(f'{url}/project/')
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        return sorted([str(r.string) for r in soup.select('.region-name')])

    def _generate_clouds(self):
        clouds = {}
        for region in self.region_list():
            config = copy.deepcopy(self.config)
            config['clouds']['ovh']['region_name'] = region
            value = yaml.dump(config)
            key = hashlib.md5(value.encode('utf-8')).hexdigest()
            clouds[key] = value
        return clouds

    def generate_clouds(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        existing = os.listdir(directory)
        all = self._generate_clouds()
        changed = False
        for new in set(all.keys()) - set(existing):
            open(f'{directory}/{new}', 'w').write(all[new])
            changed = True
        for old in set(existing) - set(all.keys()):
            old = f'{directory}/{old}'
            assert os.stat(old).st_nlink == 1, f'{old} has {os.stat(old).st_nlink} links'
            os.unlink(old)
            changed = True
        return changed

    @staticmethod
    def region_empty(origin):
        c = sh.openstack.bake('--os-cloud=ovh', _env={
            'OS_CLIENT_CONFIG_FILE': origin,
        })
        servers = c.server.list()
        images = c.image.list('--private')
        return servers.strip() == '' and images.strip() == ''

    @staticmethod
    def allocate_cloud(directory, destination):
        if os.path.exists(destination):
            return True
        for f in sorted(os.listdir(directory)):
            origin = f'{directory}/{f}'
            os.link(origin, destination)
            if (
                    os.stat(origin).st_nlink == 2 and
                    OpenStack.region_empty(origin) and
                    Heat(origin).is_working()
            ):
                return origin
            else:
                os.unlink(destination)
        return False
