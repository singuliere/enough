import os
import yaml

from enough.common.hosting import Hosting


def test_ensure_ssh_key(tmpdir):
    h = Hosting('NAME')
    h.config_dir = tmpdir
    h.ensure_ssh_key()
    assert os.path.exists(f'{tmpdir}/infrastructure_key.pub')


def test_populate_config(tmpdir):
    h = Hosting('NAME')
    h.config_dir = tmpdir
    h.populate_config()

    domain = yaml.load(open(f'{tmpdir}/inventory/group_vars/all/domain.yml'))
    assert 'letsencrypt_staging' in domain


def test_create_hosts(tmpdir, mocker):
    h = Hosting({'name': 'NAME'})
    h.config_dir = tmpdir

    mocker.patch('enough.common.openstack.Heat.get_stack_definition',
                 return_value={})

    created = [
        {'ipv4': '1.2.3.10'},
        {'ipv4': '1.2.3.11'},
        {'ipv4': '1.2.3.12'},
        {'ipv4': '1.2.3.13'},
    ]
    mocker.patch('enough.common.openstack.Stack.create_or_update',
                 side_effect=lambda: created.pop(0))

    mocker.patch('enough.common.openstack.Stack.set_public_key',
                 return_value='PUBLIC KEY CONTENT')

    h.create_hosts('PUBLIC_KEY_PATH')

    hosts = yaml.load(open(f'{tmpdir}/inventory/hosts.yml'))

    assert hosts == {
        'all': {
            'hosts': {
                'bind-host': {'ansible_host': '1.2.3.10'},
                'icinga-host': {'ansible_host': '1.2.3.11'},
                'postfix-host': {'ansible_host': '1.2.3.12'},
                'wazuh-host': {'ansible_host': '1.2.3.13'},
            },
        },
    }
