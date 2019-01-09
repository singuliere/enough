import sys

from cliff.app import App
from cliff.commandmanager import CommandManager

from enough.version import __version__


class EnoughApp(App):

    def __init__(self):
        super(EnoughApp, self).__init__(
            description='enough',
            version=__version__,
            command_manager=CommandManager('enough.cli'),
            deferred_help=True,
            )


def main(argv=sys.argv[1:]):
    myapp = EnoughApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
