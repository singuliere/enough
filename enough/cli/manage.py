from cliff.command import Command
import os
import sys


class Manage(Command):
    "Manage"

    def get_parser(self, prog_name):
        parser = super(Manage, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enough.settings')
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc
        execute_from_command_line(['enough', 'runserver'])
