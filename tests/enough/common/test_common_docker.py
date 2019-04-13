import os
from enough.common import docker
import pytest
from tests.modified_environ import modified_environ
from enough.version import __version__
from enough.common import retry


class DockerFixture(docker.Docker):

    def __init__(self, *args, **kwargs):
        # catch unintended calls to docker
        kwargs.setdefault('docker', '/bin/false')
        super(DockerFixture, self).__init__(*args, **kwargs)


def test_init():
    name = 'NAME'
    d = DockerFixture(name)
    assert d.name == name


def test_get_image_name():
    docker_name = 'DOCKER_NAME'
    suffix = 'SUFFIX'
    d = DockerFixture(docker_name)
    assert d.get_image_name(suffix) == docker_name + '_' + suffix
    assert d.get_image_name(None) == docker_name


def test_get_image_name_with_version():
    docker_name = 'DOCKER_NAME'
    suffix = 'SUFFIX'
    with modified_environ('DOCKER_HOST'):
        d = DockerFixture(docker_name)
        image_name = d.get_image_name(suffix) + ':' + str(__version__)
        assert d.get_image_name_with_version(suffix) == image_name


def test_replace_content():
    docker_name = 'DOCKER_NAME'
    with modified_environ('DOCKER_HOST'):
        d = DockerFixture(docker_name)
        before = 'Name = {{ this.get_image_name_with_version(None) }}'
        after = 'Name = ' + d.get_image_name_with_version(None)
        assert d.replace_content(before) == after


@pytest.mark.skipif('SKIP_INTEGRATION_TESTS' in os.environ, reason='skip integration test')
def test_up_no_wait(docker_name, tcp_port):
    d = docker.Docker(docker_name, port=tcp_port)
    assert d.create_image()
    d.up()
    assert d.inspect('{{ .Path }}') == ['/sbin/init']
    d.down()


@pytest.mark.skipif('SKIP_INTEGRATION_TESTS' in os.environ, reason='skip integration test')
def test_up_wait_for_services(docker_name, tcp_port):
    d = docker.Docker(docker_name, port=tcp_port)
    assert d.create_image()
    d.up_wait_for_services()
    assert '"Status":"healthy"' in d.get_logs()
    d.down()


@pytest.mark.skipif('SKIP_INTEGRATION_TESTS' in os.environ, reason='skip integration test')
def test_up_wait_for_services_fail(docker_name):
    class DockerFixtureIntegration(docker.Docker):

        def __init__(self, *args, **kwargs):
            kwargs['root'] = 'tests/enough/common/data'
            kwargs['retry'] = 2
            super().__init__(*args, **kwargs)

        def get_compose_content(self):
            f = os.path.join(self.root, 'common/data/docker-compose-fail.yml')
            return self.replace_content(open(f).read())

    d = DockerFixtureIntegration(docker_name)
    assert d.create_image()
    with pytest.raises(retry.RetryException):
        d.up_wait_for_services()
    d.down()


@pytest.mark.skipif('SKIP_INTEGRATION_TESTS' in os.environ, reason='skip integration test')
def test_create_image(docker_name):
    d = docker.Docker(docker_name)
    assert d.create_image().startswith(docker_name)
