from cliff.show import ShowOne
from cliff.command import Command

from django.conf import settings

from enough.common import openstack


def set_common_options(parser):
    parser.add_argument('name')
    return parser


class Create(ShowOne):
    "Create or update a host"

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return set_common_options(parser)

    def take_action(self, parsed_args):
        clouds_file = f'{settings.CONFIG_DIR}/inventory/group_vars/all/clouds.yml'
        s = openstack.Stack(clouds_file, openstack.Heat.get_stack_definition(parsed_args.name))
        s.set_public_key(f'{settings.CONFIG_DIR}/infrastructure_key.pub')
        s.debug = self.app.options.debug
        r = s.create_or_update()
        columns = ('name', 'user', 'port', 'ip')
        data = (parsed_args.name, 'debian', r['port'], r['ipv4'])
        return (columns, data)


class Delete(Command):
    "Delete a host"

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return set_common_options(parser)

    def take_action(self, parsed_args):
        clouds_file = f'{settings.CONFIG_DIR}/inventory/group_vars/all/clouds.yml'
        s = openstack.Stack(clouds_file, openstack.Heat.get_stack_definition(parsed_args.name))
        s.debug = self.app.options.debug
        s.delete()


class Inventory(Command):
    "Write an ansible compatible inventory of all hosts"

    def take_action(self, parsed_args):
        clouds_file = f'{settings.CONFIG_DIR}/inventory/group_vars/all/clouds.yml'
        openstack.Heat(clouds_file).write_inventory()
