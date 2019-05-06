import logging
import os
import pytest
import sh
import socket
import time
from enough.common.retry import retry
from enough.common.openstack import OpenStack


@pytest.fixture(autouse=True, scope='session')
def debug_enough():
    logging.getLogger('enough').setLevel(logging.DEBUG)


def get_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return str(port)


@pytest.fixture
def tcp_port():
    return str(get_tcp_port())


def docker_conf():
    if 'DOCKER_HOST' in os.environ:
        return {
            'namespace': 'myaccount',
        }
    else:
        return {
            'port': get_tcp_port(),
        }


@pytest.fixture
def docker_args():
    return docker_conf()


@pytest.fixture
def docker_options():
    options = []
    for k, v in docker_conf().items():
        k = k.replace('_', '-')
        options.append('--' + k)
        options.append(v)
    return options


class DockerLeftovers(Exception):
    pass


@retry(DockerLeftovers, tries=7)
def docker_cleanup(prefix):
    leftovers = []
    for container in sh.docker.ps('--all', '--format', '{{ .Names }}', _iter=True):
        container = container.strip()
        if prefix in container:
            sh.docker.rm('-f', container, _ok_code=[0, 1])
            leftovers.append('container(' + container + ')')
    for network in sh.docker.network.ls('--format', '{{ .Name }}', _iter=True):
        network = network.strip()
        if prefix in network:
            sh.docker.network.rm(network, _ok_code=[0, 1])
            leftovers.append('network(' + network + ')')
    for image in sh.docker.images('--format', '{{ .Repository }}:{{ .Tag }}', _iter=True):
        image = image.strip()
        if image.startswith(prefix):
            sh.docker.rmi('--no-prune', image, _ok_code=[0, 1])
            leftovers.append('image(' + image + ')')
    if leftovers:
        raise DockerLeftovers('scheduled removal of ' + ' '.join(leftovers))


@pytest.fixture
def docker_name():
    prefix = 'enough_test_' + str(int(time.time()))
    if 'DOCKER_HOST' not in os.environ:
        sh.docker.swarm.init(_ok_code=[1, 0])
    yield prefix
    logging.getLogger('sh').setLevel(logging.CRITICAL)
    docker_cleanup(prefix)


@pytest.fixture
def openstack_name():
    prefix = 'enough_test_' + str(int(time.time()))
    yield prefix
    logging.getLogger('sh').setLevel(logging.CRITICAL)
    o = OpenStack('inventory/group_vars/all/clouds.yml')
    o.destroy_everything(prefix)
