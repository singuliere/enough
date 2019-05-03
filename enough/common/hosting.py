from django.conf import settings
from enough.common import bind, openstack
import os
import sh


class Hosting(object):

    def __init__(self, name):
        self.name = name
        self.domain = f"{name}.d.{settings.ENOUGH_DOMAIN}"
        self.config_dir = os.path.expanduser(f'~/.enough/{self.domain}')
        d = f'{self.config_dir}/group_vars/all'
        if not os.path.exists(d):
            os.makedirs(d)
        self.clouds_file = f'{d}/clouds.yml'

    def ensure_ssh_key(self):
        path = f'{self.config_dir}/infrastructure_key'
        if not os.path.exists(path):
            sh.ssh_keygen('-f', path, '-N', '', '-b', '4096', '-t', 'rsa')
        return path

    def create_or_upgrade(self):
        assert openstack.OpenStack.allocate_cloud(
            f'{settings.CONFIG_DIR}/api/hosting/all', self.clouds_file)
        s = openstack.Stack(self.clouds_file, openstack.Heat.get_stack_definition('bind-host'))
        key = self.ensure_ssh_key()
        s.set_public_key(f'{key}.pub')
        bind_host = s.create_or_update()
        bind.delegate_dns(f'd.{settings.ENOUGH_DOMAIN}', self.name, bind_host['ipv4'])

    def delete(self):
        s = openstack.Stack(self.clouds_file, openstack.Heat.get_stack_definition('bind-host'))
        s.delete()
        return {}
