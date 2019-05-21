from cliff.show import ShowOne
from cliff.command import Command

from enough.common.host import host_factory
from enough.common import tcp


def set_common_options(parser):
    parser.add_argument('--driver', default='openstack')
    return parser


class Create(ShowOne):
    "Create or update a host"

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('name')
        return set_common_options(parser)

    def take_action(self, parsed_args):
        args = vars(self.app.options)
        args.update(vars(parsed_args))
        args['port'] = tcp.free_port()
        host = host_factory(**args)
        host.create_or_update()
        columns = ('name', 'user', 'port', 'ip')
        data = (parsed_args.name, 'debian', args['port'], '0.0.0.0')
        return (columns, data)


class Delete(Command):
    "Delete a host"

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('name')
        return set_common_options(parser)

    def take_action(self, parsed_args):
        host = host_factory(**vars(parsed_args))
        host.delete()


class Inventory(Command):
    "Write an ansible compatible inventory of all hosts"

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return set_common_options(parser)

    def take_action(self, parsed_args):
        host = host_factory(**vars(parsed_args))
        host.write_inventory()
