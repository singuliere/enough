from enough.common.host import host_factory
from tests import conftest


def test_docker_create_or_update(docker_name, tcp_port):
    host = host_factory(**{
        'driver': 'docker',
        'name': docker_name,
        'domain': docker_name,
        'port': tcp_port,
    })
    host.create_or_update()
    assert '"Status":"healthy"' in host.d.get_logs()
    host.d.down()


def test_docker_create_or_update_same_network(docker_name):
    name1 = f'{docker_name}1'
    port1 = conftest.get_tcp_port()
    host1 = host_factory(**{
        'driver': 'docker',
        'name': name1,
        'domain': docker_name,
        'port': port1,
    })
    host1.create_or_update()
    assert '"Status":"healthy"' in host1.d.get_logs()

    name2 = f'{docker_name}2'
    port2 = conftest.get_tcp_port()
    host2 = host_factory(**{
        'driver': 'docker',
        'name': name2,
        'domain': docker_name,
        'port': port2,
    })
    host2.create_or_update()
    assert '"Status":"healthy"' in host2.d.get_logs()

    assert host2.d.docker_compose.exec('-T', name2, 'ping', '-c1', name1)
