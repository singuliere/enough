from __future__ import print_function
from io import StringIO
import jinja2
import logging
import os
import sys
import sh
import tempfile

from enough.version import __version__
from enough.common.retry import retry, RetryException

log = logging.getLogger(__name__)


class Docker(object):

    def __init__(self, name, **kwargs):
        self.bake_docker(kwargs.get('docker'))
        self.root = kwargs.get('root', os.path.join(os.path.dirname(__file__), '..'))
        self.name = name
        self.port = kwargs.get('port', '8000')
        self.retry = kwargs.get('retry', 9)
        self.domain = kwargs.get('domain', 'enough.community')
        self.bake_docker_compose(kwargs.get('docker_compose'))

    def bake_docker(self, docker):
        cmd = docker or 'docker'
        self.docker = sh.Command(cmd).bake(_truncate_exc=False)
        # .bake(_out=sys.stdout, _err=sys.stderr, )

    def bake_docker_compose(self, docker_compose):
        content = self.get_compose_content()
        if log.getEffectiveLevel() <= logging.DEBUG:
            # do not use log.debug() because the output is unreadable on a single line
            # and multiline logging is bad practice
            print(content)
        compose = tempfile.NamedTemporaryFile()
        compose.write(content.encode('utf-8'))
        compose.flush()
        cmd = docker_compose or 'docker-compose'
        self.docker_compose = sh.Command(cmd).bake('-f', compose.name, _truncate_exc=False)
        self.compose_file = compose  # so that it is kept until self is deleted

    def get_compose_content(self):
        f = os.path.join(self.root, 'common/data/docker-compose.yml')
        return self.replace_content(open(f).read())

    def replace_content(self, content):
        return jinja2.Template(content).render(this=self)

    def get_ports(self):
        return str(self.port) + ':8000'

    def create_image(self):
        dockerfile = os.path.join(self.root, 'common/data/base.dockerfile')
        return self._create_image('base', '-f', dockerfile, '.')

    def _create_image(self, suffix, *args):
        name = self.get_image_name_with_version(suffix)
        build_args = ['--quiet', '--tag', name]
        self.docker.build(build_args + list(args))
        self.docker.tag(name, self.get_image_name(suffix))
        return name

    def get_image_name(self, suffix):
        if suffix:
            return self.name + '_' + suffix
        else:
            return self.name

    def get_image_name_with_version(self, suffix):
        return self.get_image_name(suffix) + ':' + str(__version__)

    def down(self):
        self.docker_compose('down')

    def up_wait_for_services(self):
        self.up()
        try:
            self.wait_for_services()
        except RetryException:
            self.print_logs()
            raise

    def up(self):
        self.docker_compose('up', '-d')

    def inspect(self, format):
        ids = self.docker_compose('ps', '-q', _iter=True)
        results = []
        for id in ids:
            id = id.strip()
            result = StringIO()
            self.docker('inspect', f'--format={format}', id, _out=result)
            results.append(result.getvalue().strip())
        return results

    def wait_for_services(self):
        @retry(AssertionError, tries=self.retry)
        def wait():
            results = self.inspect('{{ .State.Health.Status }}')
            assert all([x.strip() == 'healthy' for x in results]), str(results)
            log.info("enough service " + self.name + " is healthy")
        wait()

    def get_logs(self):
        result = StringIO()
        print(f"docker compose logs {self.name}\n", file=result)
        self.docker_compose('logs', _out=result)
        print(str(self.inspect('{{ json .State.Health }}')))
        result.write(str(self.inspect('{{ json .State.Health }}')))
        return result.getvalue()

    def print_logs(self):
        print(self.get_logs(), file=sys.stderr)
