import os
import sh

from cliff.command import Command

from enough.common.docker import Docker


class Build(Command):
    "Build the enough docker image."

    class DockerEnough(Docker):

        def create_image(self):
            name = super().create_image()
            sh.rm('-fr', 'dist')
            sh.python('setup.py', '--quiet', 'sdist')
            dockerfile = os.path.join(self.root, 'internal/data/enough-source.dockerfile')
            return self._create_image(None,
                                      '--build-arg', f'IMAGE_NAME={name}',
                                      '-f', dockerfile, '.')

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('--name', default='enough')
        return parser

    def take_action(self, parsed_args):
        Build.DockerEnough(parsed_args.name).create_image()


class Create(Command):
    "Create the enough service."

    class DockerEnough(Docker):

        def get_compose_content(self):
            f = os.path.join(self.root, 'internal/data/docker-compose.yml')
            return self.replace_content(open(f).read())

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('--name', default='enough')
        parser.add_argument('--port', default='8000')
        return parser

    def take_action(self, parsed_args):
        args = vars(parsed_args)
        Create.DockerEnough(**args).up_wait_for_services()
