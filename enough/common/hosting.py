from django.conf import settings
from enough.common import bind, openstack
import textwrap
import os
import sh

from enough.common import ansible_utils


class Hosting(object):

    def __init__(self, name):
        self.name = name
        self.domain = f"{name}.d.{settings.ENOUGH_DOMAIN}"
        self.config_dir = settings.CONFIG_DIR
        d = f'{self.config_dir}/inventory/group_vars/all'
        if not os.path.exists(d):
            os.makedirs(d)
        self.clouds_file = f'{d}/clouds.yml'

    def ensure_ssh_key(self):
        path = f'{self.config_dir}/infrastructure_key'
        if not os.path.exists(path):
            sh.ssh_keygen('-f', path, '-N', '', '-b', '4096', '-t', 'rsa')
        return path

    def create_hosts(self, public_key):
        names = ('bind-host', 'icinga-host', 'postfix-host', 'wazuh-host')
        h = openstack.Heat(self.clouds_file)
        inventory = h.to_inventory(h.create_or_update(names, public_key))
        d = f'{self.config_dir}/inventory'
        if not os.path.exists(d):
            os.makedirs(d)
        open(f'{d}/hosts.yml', 'w').write(inventory)
        return names

    def populate_config(self):
        d = f'{self.config_dir}/inventory/group_vars/all'
        if not os.path.exists(d):
            os.makedirs(d)
        open(f'{d}/private-key.yml', 'w').write(textwrap.dedent(f"""\
        ---
        ssh_private_keyfile: {self.config_dir}/infrastructure_key
        """))

        staging = os.path.exists('/etc/ssl/certs/fakelerootx1.pem')

        open(f'{d}/domain.yml', 'w').write(textwrap.dedent(f"""\
        ---
        domain: {self.domain}
        production_domain: {self.domain}
        letsencrypt_staging: {staging}
        """))

    def create_or_upgrade(self):
        assert openstack.OpenStack.allocate_cloud(
            f'{settings.CONFIG_DIR}/api/hosting/all', self.clouds_file)
        s = openstack.Stack(self.clouds_file,
                            openstack.Heat.get_stack_definition('bind-host'))
        key = self.ensure_ssh_key()
        s.set_public_key(f'{key}.pub')
        bind_host = s.create_or_update()
        bind.delegate_dns(f'd.{settings.ENOUGH_DOMAIN}', self.name, bind_host['ipv4'])
        names = self.create_hosts(f'{key}.pub')
        self.populate_config()
        ansible_utils.bake_ansible_playbook()(
            '-i', f'{self.config_dir}/inventory',
            '--private-key', key,
            '--limit', ','.join(names + ('localhost',)),
            'playbook.yml')

    def delete(self):
        names = ('bind-host', 'icinga-host', 'postfix-host', 'wazuh-host')
        for name in names:
            s = openstack.Stack(self.clouds_file,
                                openstack.Heat.get_stack_definition(name))
            s.delete()
        return {}
