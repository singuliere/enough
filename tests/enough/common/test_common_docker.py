import os
import sh
from enough.common import docker
import pytest
from tests.modified_environ import modified_environ
from enough.version import __version__


class DockerFixture(docker.Docker):

    def __init__(self, *args, **kwargs):
        # catch unintended calls to docker
        kwargs.setdefault('docker', '/bin/false')
        super(DockerFixture, self).__init__(*args, **kwargs)


def test_init():
    name = 'NAME'
    d = DockerFixture(name)
    assert d.name == name


def test_is_local():
    with modified_environ('DOCKER_HOST'):
        assert DockerFixture('NAME').is_local()
    with modified_environ(DOCKER_HOST="somehost"):
        assert not DockerFixture('NAME').is_local()


def test_get_repository_name():
    docker_name = 'DOCKER_NAME'
    suffix = 'SUFFIX'
    d = DockerFixture(docker_name)
    assert d.get_repository_name(suffix) == docker_name + '_' + suffix
    assert d.get_repository_name(None) == docker_name


def test_get_image_name():
    docker_name = 'DOCKER_NAME'
    suffix = 'SUFFIX'
    with modified_environ('DOCKER_HOST'):
        d = DockerFixture(docker_name)
        repository = d.get_repository_name(suffix)
        image_name = repository + ':' + str(__version__)
        assert d.get_image_name(suffix) == image_name

    with modified_environ(DOCKER_HOST="somehost"):
        registry = 'REGISTRY'
        namespace = 'NAMESPACE'
        d = DockerFixture(docker_name,
                          registry=registry,
                          namespace=namespace)
        repository = d.get_repository_name(suffix)
        assert d.get_image_name(suffix) == registry + '/' + namespace + '/' + image_name


def test_get_requests_session():
    docker_name = 'DOCKER_NAME'
    with modified_environ('DOCKER_HOST'):
        d = DockerFixture(docker_name)
        s = d.get_requests_session()
        assert s.trust_env is False
        # verify session is cached
        assert d.get_requests_session() == s
    with modified_environ(DOCKER_HOST="somehost"):
        d = DockerFixture(docker_name)
        s = d.get_requests_session()
        assert s.trust_env is True


def test_swarm_init():
    docker_name = 'DOCKER_NAME'
    with modified_environ('DOCKER_HOST'):
        d = DockerFixture(docker_name,
                          docker='tests/enough/common/bin/test_swarm_init_docker/inactive.sh')
        assert d.swarm_init() is True

        d = DockerFixture(docker_name,
                          docker='tests/enough/common/bin/test_swarm_init_docker/active.sh')
        assert d.swarm_init() is False

    with modified_environ(DOCKER_HOST="somehost"):
        d = DockerFixture(docker_name)
        assert d.swarm_init() is None


def test_replace_content():
    docker_name = 'DOCKER_NAME'
    with modified_environ('DOCKER_HOST'):
        d = DockerFixture(docker_name)
        before = 'Name = {{ this.get_image_name(None) }}'
        after = 'Name = ' + d.get_image_name(None)
        assert d.replace_content(before) == after


class DockerFixtureIntegration(docker.Docker):

    def __init__(self, *args, **kwargs):
        super(DockerFixtureIntegration, self).__init__(*args, **kwargs)
        self.root = 'tests/enough/common/data'

    def get_compose_content(self):
        f = os.path.join(self.root, 'common/data/docker-compose.yml')
        return self.replace_content(open(f).read())


@pytest.mark.skipif('SKIP_INTEGRATION_TESTS' in os.environ, reason='skip integration test')
def test_inner_deploy(docker_name, tcp_port):
    d = DockerFixtureIntegration(docker_name)
    assert d.create_image()
    d.port = tcp_port
    stack = d._deploy()
    assert stack
    ls = d.docker.service.ls('--filter', 'Name=' + stack, '--format', '{{ json . }}')
    assert len(list(ls)) == 1


@pytest.mark.skipif('SKIP_INTEGRATION_TESTS' in os.environ, reason='skip integration test')
def test_deploy_wait_for_service(docker_name, tcp_port):
    d = DockerFixtureIntegration(docker_name)
    assert d.deploy_wait_for_service({'port': tcp_port})
    assert 'docker service logs' in d.get_stack_logs()
    d.rm()


@pytest.mark.skipif('SKIP_INTEGRATION_TESTS' in os.environ, reason='skip integration test')
def test_get_network_peer_and_get_host_port(docker_name):
    try:
        sh.docker.stack.deploy('-c', 'tests/enough/common/get_network_peer/docker-compose.yml',
                               docker_name)
        d = DockerFixtureIntegration(docker_name)
        assert len(d.get_network_peer().split('.')) == 4
        ip_service = 'ip_service'
        port = '8080'
        assert d.get_host_port(ip_service, port) == ip_service
        assert d.get_host_port(None, port).endswith(':' + str(port))
    finally:
        sh.docker.stack.rm(docker_name)


@pytest.mark.skipif('SKIP_INTEGRATION_TESTS' in os.environ, reason='skip integration test')
def test_create_image(docker_name):
    d = DockerFixtureIntegration(docker_name)
    assert d.create_image().startswith(docker_name)
