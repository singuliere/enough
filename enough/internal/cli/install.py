import logging
import os

from cliff.command import Command
from enough.version import __version__


class InstallScript(Command):
    "A bash script to install enough."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(InstallScript, self).get_parser(prog_name)
        parser.add_argument('--script', action='store_true')
        parser.add_argument('--service', action='store_true')
        parser.add_argument('--no-version', action='store_true')
        return parser

    def version(self, parsed_args):
        if parsed_args.no_version:
            return ''
        else:
            return f':{__version__}'

    def script(self, parsed_args):
        i = os.path.join(os.path.dirname(__file__), '../data/install.sh')
        content = open(i).read()
        print(content.replace('%version%', self.version(parsed_args)))

    def service(self, parsed_args):
        i = os.path.join(os.path.dirname(__file__), '../../api/data/enough.service')
        content = open(i).read()
        print(content.replace('%version%', self.version(parsed_args)))

    def function(self, parsed_args):
        print('function enough() {')
        self.script(parsed_args)
        print('}')

    def take_action(self, parsed_args):
        if parsed_args.script:
            self.script(parsed_args)
        elif parsed_args.service:
            self.service(parsed_args)
        else:
            self.function(parsed_args)
