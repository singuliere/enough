import sys

from cliff.app import App
from cliff.commandmanager import CommandManager

from enough.version import __version__


class InternalApp(App):

    def __init__(self):
        super(InternalApp, self).__init__(
            description='internal enough',
            version=__version__,
            command_manager=CommandManager('enough.internal.cli'),
            deferred_help=True,
            )


def main(argv=sys.argv[1:]):
    myapp = InternalApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
