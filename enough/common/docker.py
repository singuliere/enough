from __future__ import print_function
from io import StringIO
import json
import jinja2
import logging
import os
import requests
import sys
import sh
import tempfile
from enough.version import __version__
from enough.common.retry import retry, RetryException

log = logging.getLogger(__name__)


class Docker(object):

    def __init__(self, name, **kwargs):
        self.bake_docker(kwargs.get('docker'))
        self.root = os.path.join(os.path.dirname(__file__), '..')
        self.name = name
        self.session = None
        self.local = "DOCKER_HOST" not in os.environ
        if not self.is_local():
            self.registry = kwargs.get('registry')
            self.namespace = kwargs.get('namespace')
            self.user = kwargs.get('user')
            self.password = kwargs.get('password')
        self.confdir = kwargs.get('confdir')

    def bake_docker(self, docker):
        cmd = docker or 'docker'
        self.docker = sh.Command(cmd).bake(_truncate_exc=False)
        # .bake(_out=sys.stdout, _err=sys.stderr, )

    def get_or_create_password_file(self, filename):
        path = os.path.abspath('{confdir}/{filename}'.format(
            confdir=self.confdir,
            filename=filename))
        if not os.path.exists(path):
            open(path, 'w').write('enough')
        return path

    def is_local(self):
        return self.local

    def get_compose_content(self):
        assert 0  # pragma: no cover

    def replace_content(self, content):
        return jinja2.Template(content).render(this=self)

    def get_ports(self):
        return str(self.port) + ':3000' if self.is_local() else '3000'

    def deploy(self, args):
        self.port = args.get('port')
        self.ip_service = args.get('ip_service')
        if self.is_local():
            self.network_definition = ''
        else:
            self.network_definition = '{external: {name: external_network}}'

        self.swarm_init()
        self.create_image()
        self._deploy()

        return self.get_host_port(self.ip_service, self.port)

    def create_image(self):
        dockerfile = os.path.join(self.root, 'common/data/base.dockerfile')
        return self._create_image('base', '-f', dockerfile, '.')

    def _create_image(self, suffix, *args):
        name = self.get_image_name(suffix)
        build_args = ['--quiet', '--tag', name]
        self.docker.build(build_args + list(args))
        self._push_image(suffix)
        return name

    def get_network_peer(self):
        @retry(UnboundLocalError, tries=4)
        def get_network_id():
            networks = self.docker.network.ls('--format', '{{ json . }}', _iter=True)
            for network in networks:
                network = json.loads(network)
                if self.name in network["Name"]:
                    network_id = network["ID"]
                    return network_id
        network_id = get_network_id()
        inspection = StringIO()

        @retry(sh.ErrorReturnCode_1, tries=4)
        def get_peer():
            self.docker.network.inspect('--format', '{{ (index .Peers 0).IP }}',
                                        network_id, _out=inspection)
        get_peer()
        return inspection.getvalue().strip()

    def get_host_port(self, ip_service, port):
        if ip_service:
            return ip_service
        else:
            ip_service = self.get_network_peer()
            return '{ip_service}:{port}'.format(ip_service=ip_service,
                                                port=port)

    def get_repository_name(self, suffix):
        if suffix:
            return self.name + '_' + suffix
        else:
            return self.name

    def get_image_name(self, suffix):
        repository = self.get_repository_name(suffix)
        name = repository + ':' + str(__version__)
        if self.is_local():
            return name
        else:
            return self.registry + '/' + self.namespace + '/' + name

    def get_requests_session(self):
        if self.session is None:
            self.session = requests.Session()
            if self.is_local():
                self.session.trust_env = False
        return self.session

    def rm(self):
        self.docker.stack.rm(self.name)

    def deploy_wait_for_service(self, args):
        host_port = self.deploy(args)
        try:
            self.wait_for_service()
            return host_port
        except RetryException:
            self.print_stack_logs()
            raise

    def swarm_init(self):
        if not self.is_local():
            return None
        state = self.docker.info('--format', '{{ .Swarm.LocalNodeState }}', _iter=True)
        if state.next().strip() == 'inactive':
            self.docker.swarm.init()
            return True
        return False

    def _push_image(self, suffix):
        if not self.is_local():
            self.create_repository(suffix)
            name = self.get_full_image_name(suffix)
            self.docker.push(name)

    def _deploy(self):
        content = self.get_compose_content()
        if log.getEffectiveLevel() <= logging.DEBUG:
            # do not use log.debug() because the output is unreadable on a single line
            # and multiline logging is bad practice
            print(content)
        with tempfile.NamedTemporaryFile() as compose:
            compose.write(content.encode('utf-8'))
            compose.flush()
            self.docker.stack.deploy('-c', compose.name, self.name)
        return self.name

    def create_repository(self, suffix):
        kwargs = {}
        if 'DOCKER_CERT_PATH' in os.environ:
            kwargs['verify'] = os.environ['DOCKER_CERT_PATH'] + "/ca.pem"
        name = self.get_repostiry_name(suffix)
        res = self.get_requets_session().post(
            'https://' + self.registry + '/api/v0/repositories/' + self.namespace,
            auth=(self.user, self.password),
            json={'name': name, 'visibility': 'public'},
            **kwargs)
        log.debug("Creating repository " + self.namespace + "/" + name)
        if res.status_code == 400 and res.json()["errors"][0]["code"] == "REPOSITORY_EXISTS":
            log.debug("already exists")
        elif res.status_code != 201:
            res.raise_for_status()

    @retry(AssertionError, tries=9)
    def wait_for_service(self):
        replica = self.docker.service.ls('--filter',
                                         'Name=' + self.name,
                                         '--format', '{{ .Replicas }}',
                                         _iter=True)
        nb_up, nb_tot = replica.next().strip().split("/")
        assert nb_up == nb_tot
        log.info("Docker stack " + self.name + " is up")

    def get_stack_logs(self):
        result = StringIO()
        print(u"docker stack ps --no-trunc " + self.name, file=result)
        self.docker.stack.ps('--no-trunc', self.name, _out=result)
        services = self.docker.stack.ps('--format', '{{ .ID }}', self.name, _iter=True)
        for service in services:
            id = service.strip()
            print("docker service logs " + id, file=result)
            self.docker.service.logs('--timestamps', '--details', id, _out=result)
        return result.getvalue()

    def print_stack_logs(self):
        print(self.get_stack_logs(), file=sys.stderr)
