from django.conf import settings
from enough.common import openstack, docker
from abc import ABC, abstractmethod


class Host(ABC):

    @abstractmethod
    def create_or_update(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def write_inventory(self):
        pass


class HostDocker(Host):

    def create_or_upate(self):
        pass

    def delete(self):
        pass

    def write_inventory(self):
        pass


class HostOpenStack(Host):

    def __init__(self, **kwargs):
        self.args = kwargs
        self.clouds_file = f'{settings.CONFIG_DIR}/inventory/group_vars/all/clouds.yml'

    def create_or_update(self):
        s = openstack.Stack(self.clouds_file, openstack.Heat.get_stack_definition(self.args['name']))
        s.set_public_key(f'{settings.CONFIG_DIR}/infrastructure_key.pub')
        return s.create_or_update(self)

    def delete(self):
        s = openstack.Stack(self.clouds_file, openstack.Heat.get_stack_definition(self.args['name']))
        s.delete()

    def write_inventory(self):
        openstack.Heat(self.clouds_file).write_inventory()


def host_factory(**kwargs):
    if kwargs['driver'] == 'openstack':
        return HostOpenStack(**kwargs)
    else:
        return HostDocker(**kwargs)
