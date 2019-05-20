import os
import yaml
from enough.internal.cmd import main


def test_inventory(tmpdir, mocker):
    mocker.patch('enough.settings.CONFIG_DIR', str(tmpdir))
    mocker.patch('enough.common.openstack.Stack.list',
                 return_value=['some-host'])
    ip = '1.2.3.4'
    mocker.patch('enough.common.openstack.Heat.create_or_update',
                 return_value={
                     'some-host': {'ipv4': ip},
                 })

    assert main(['--debug', 'host', 'inventory']) == 0
    assert os.path.exists(f'{tmpdir}/inventory/hosts.yml')
    h = yaml.load(open(f'{tmpdir}/inventory/hosts.yml'))
    assert h['all']['hosts']['some-host']['ansible_host'] == ip
