import sh
from enough.internal.cmd import main
from enough.common.docker import Docker
from io import StringIO


def test_enough_docker_image(docker_name):
    assert main(['--debug', 'build', 'enough', 'image', '--name', docker_name]) == 0
    image_name = Docker(docker_name).get_image_name(suffix=None)
    out = StringIO()
    sh.docker('image', 'ls', '--filter', 'reference=' + image_name,
              '--format', '{{ .Repository }}:{{ .Tag }}', _out=out)
    assert out.getvalue().strip() == image_name
