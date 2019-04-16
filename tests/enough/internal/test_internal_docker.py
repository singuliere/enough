import sh
from enough.internal.cmd import main
from enough.common.docker import Docker
from io import StringIO


def test_enough_docker_image(docker_name):
    assert main(['--debug', 'build', 'image', '--name', docker_name]) == 0
    image_name = Docker(docker_name,
                        domain='enough.community').get_image_name_with_version(suffix=None)
    out = StringIO()
    sh.docker('image', 'ls', '--filter', 'reference=' + image_name,
              '--format', '{{ .Repository }}:{{ .Tag }}', _out=out)
    assert out.getvalue().strip() == image_name

    image_name = Docker(docker_name,
                        domain='enough.community').get_image_name(suffix=None)
    out = StringIO()
    sh.docker('image', 'ls', '--filter', 'reference=' + image_name + ':latest',
              '--format', '{{ .Repository }}', _out=out)
    assert out.getvalue().strip() == image_name


def test_enough_docker_service(docker_name, docker_options):
    assert main(['build', 'image', '--name', docker_name]) == 0
    assert main(['--debug', 'create', 'service', '--name', docker_name] + docker_options) == 0
    for name in sh.docker.ps('--format', '{{ .Names }}', _iter=True):
        if docker_name in name:
            return
    assert 0, f'docker stack ls does not show {docker_name}'
