from enough import configuration
from cliff.command import Command
import argparse
import os


class Manage(Command):
    "Manage"

    def get_parser(self, prog_name):
        parser = super(Manage, self).get_parser(prog_name)
        parser.add_argument('args', nargs=argparse.REMAINDER)
        return parser

    def take_action(self, parsed_args):
        d = configuration.get_directory(self.app.options.domain)
        os.environ.setdefault('ENOUGH_BASE_DIR', d)
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enough.settings')
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc
        execute_from_command_line(['enough', *parsed_args.args])
