import os
import sh

from cliff.command import Command

from enough.common.docker import Docker


class DockerEnough(Docker):

    def create_image(self):
        name = super(DockerEnough, self).create_image()
        sh.rm('-fr', 'dist')
        sh.python('setup.py', '--quiet', 'sdist')
        dockerfile = os.path.join(self.root, 'internal/data/enough.dockerfile')
        return self._create_image(None, '--build-arg', 'IMAGE_NAME=' + name, '-f', dockerfile, '.')


class Build(Command):
    "Build the enough docker image."

    def get_parser(self, prog_name):
        parser = super(Build, self).get_parser(prog_name)
        parser.add_argument('--name', default='enough')
        return parser

    def take_action(self, parsed_args):
        DockerEnough(parsed_args.name).create_image()
