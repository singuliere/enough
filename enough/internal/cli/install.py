import logging
import os

from cliff.command import Command
from enough.version import __version__


class InstallScript(Command):
    "A bash script to install enough."

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        i = os.path.join(os.path.dirname(__file__), '../data/install.sh')
        content = open(i).read()
        print(content.replace('%version%', __version__))
