import base64
from bs4 import BeautifulSoup
import copy
import hashlib
from io import StringIO
import json
import logging
import os
import requests
import sh
import textwrap
import time
import yaml

from enough import settings
from enough.common.retry import retry


class Stack(object):

    def __init__(self, config_file, definition=None):
        log = logging.getLogger(__name__)
        self.h = sh.openstack.bake(
            '--os-cloud=ovh',
            _tee=True,
            _out=lambda x: log.info(x.strip()),
            _err=lambda x: log.info(x.strip()),
            _env={'OS_CLIENT_CONFIG_FILE': config_file},
        )
        self.definition = definition
        self.debug = False

    def get_template(self):
        return f'{settings.SHARE_DIR}/molecule/infrastructure/template-host.yaml'

    def set_public_key(self, path):
        self.public_key = open(path).read().strip()

    def _create_or_update(self, action):
        d = self.definition
        parameters = [
            f'--parameter=public_key={self.public_key}',
        ]
        if 'flavor' in d:
            parameters.append(f'--parameter=flavor={d["flavor"]}')
        if 'port' in d:
            parameters.append(f'--parameter=port={d["port"]}')
        if 'volumes' in d and int(d['volumes'][0]['size']) > 0:
            parameters.append(f"--parameter=volume_size={d['volumes'][0]['size']}")
            parameters.append(f"--parameter=volume_name={d['volumes'][0]['name']}")
        self.h.stack(action, d['name'],
                     '--wait', '--timeout=600',
                     '--template', self.get_template(),
                     *parameters)
        return self.get_output()

    def get_output(self):
        r = self.h.stack('output', 'show', '--format=value', '-c=output', '--all',
                         self.definition['name'])
        return json.loads(r.stdout)['output_value']

    def list(self):
        return [
            s.strip() for s in
            self.h.stack.list('--format=value', '-c', 'Stack Name', _iter=True)
        ]

    def create_or_update(self):
        if self.definition['name'] in self.list():
            action = 'update'
        else:
            action = 'create'
        return self._create_or_update(action)

    def delete(self):
        name = self.definition['name']
        if name not in self.list():
            return

        self.h.stack.delete('--yes', '--wait', name)

        @retry(AssertionError, 9)
        def wait_is_deleted():
            assert name not in self.list(), f'{name} deletion in progress'
        wait_is_deleted()


class Heat(object):

    def __init__(self, config_file):
        self.clouds_file = config_file
        self.debug = False
        log = logging.getLogger(__name__)
        self.h = sh.openstack.bake(
            '--os-cloud=ovh',
            _tee=True,
            _out=lambda x: log.info(x.strip()),
            _err=lambda x: log.info(x.strip()),
            _env={'OS_CLIENT_CONFIG_FILE': config_file},
        )

    @staticmethod
    def get_stack_definitions():
        r = sh.ansible_inventory('-i', f'{settings.SHARE_DIR}/inventory',
                                 '-i', f'{settings.CONFIG_DIR}/inventory',
                                 '--vars', '--list')
        inventory = json.loads(r.stdout)
        return inventory['_meta']['hostvars']

    @staticmethod
    def get_stack_definition(host):
        h = Heat.get_stack_definitions()[host]
        definition = {
            'name': host,
            'port': h.get('ansible_port', '22'),
            'flavor': h.get('openstack_flavor', 's1-2'),
        }
        if 'openstack_volumes' in h:
            definition['volumes'] = h['openstack_volumes']
        return definition

    def is_working(self):
        # retry to verify the API is stable
        for _ in range(5):
            try:
                self.h.stack.list()
            except sh.ErrorReturnCode_1:
                return False
        return True

    def create_or_update(self, names, public_key):
        r = {}
        for name in names:
            s = Stack(self.config_file, Heat.get_stack_definition(name))
            s.set_public_key(public_key)
            r[name] = s.create_or_update()
        return r

    def to_inventory(self, stacks):
        hosts = {}
        for name, info in stacks.items():
            hosts[name] = {
                'ansible_host': info['ipv4'],
            }
        return yaml.dump(
            {
                'all': {
                    'hosts': hosts,
                },
            }
        )

    def write_inventory(self):
        names = Stack(self.clouds_file).list()
        inventory = self.to_inventory(self.create_or_update(names))
        d = f'{settings.CONFIG_DIR}/inventory'
        if not os.path.exists(d):
            os.makedirs(d)
        open(f'{d}/hosts.yml', 'w').write(inventory)

    def create_test_subdomain(self, domain):
        # exclusively when running from molecule
        assert os.path.exists('molecule.yml')
        d = f"{settings.CONFIG_DIR}/inventory/group_vars/all"
        assert os.path.exists(d)
        if 'bind-host' not in Stack(self.clouds_file).list():
            return None
        s = Stack(self.clouds_file, Heat.get_stack_definition('bind-host'))
        s.set_public_key(f'{settings.CONFIG_DIR}/infrastructure_key.pub')
        bind_host = s.create_or_update()

        # reverse so the leftmost part varies, for human readability
        s = str(int(time.time()))[::-1]
        subdomain = base64.b32encode(s.encode('ascii')).decode('ascii').lower()

        fqdn = f'{subdomain}.test.{domain}'

        token = os.environ['ENOUGH_API_TOKEN']

        r = requests.post(f'https://api.{domain}/delegate-test-dns/',
                          headers={'Authorization': f'Token {token}'},
                          json={
                              'name': subdomain,
                              'ip': bind_host['ipv4'],
                          })
        r.raise_for_status()
        open(f'{d}/domain.yml', 'w').write(textwrap.dedent(f"""\
        ---
        domain: {fqdn}
        """))
        return fqdn


class OpenStackLeftovers(Exception):
    pass


class OpenStack(object):

    def __init__(self, config_file):
        self.config_file = config_file
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

    @retry(OpenStackLeftovers, tries=7)
    def destroy_everything(self, prefix):
        log = logging.getLogger(__name__)
        s = sh.openstack.bake(
            '--os-cloud=ovh',
            _tee=True,
            _out=lambda x: log.info(x.strip()),
            _err=lambda x: log.info(x.strip()),
            _env={'OS_CLIENT_CONFIG_FILE': self.config_file},
        )
        leftovers = []
        for stack in s.stack.list('--format=value', '-c', 'Stack Name', _iter=True):
            stack = stack.strip()
            if prefix is None or prefix in stack:
                leftovers.append(f'stack({stack})')
                try:
                    out = StringIO()
                    s.stack.delete('--yes', '--wait', stack, _out=out, _err_to_out=True)
                except sh.ErrorReturnCode_1:
                    value = out.getvalue()
                    if (('Stack not found' not in value) and
                            ('could not be found' not in value)):
                        raise

        for image in s.image.list('--private', '--format=value', '-c', 'Name', _iter=True):
            image = image.strip()
            if prefix is None or prefix in image:
                leftovers.append(f'image({image})')
                s.image.delete(image)

        if leftovers:
            raise OpenStackLeftovers('scheduled removal of ' + ' '.join(leftovers))

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
        log = logging.getLogger(__name__)
        c = sh.openstack.bake(
            '--os-cloud=ovh',
            _tee=True,
            _out=lambda x: log.info(x.strip()),
            _err=lambda x: log.info(x.strip()),
            _env={'OS_CLIENT_CONFIG_FILE': origin},
        )
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
