import os
import pytest
import sh
import yaml
import requests_mock as requests_mock_module

from tests.modified_environ import modified_environ

from enough.common.openstack import Stack, Heat, OpenStack


#
# Stack
#
@pytest.mark.skipif('SKIP_OPENSTACK_INTEGRATION_TESTS' in os.environ,
                    reason='skip integration test')
def test_stack_create_or_update(openstack_name):
    d = {
        'name': openstack_name,
        'flavor': 's1-2',
        'port': '22',
        'volumes': [
            {
                'size': '1',
                'name': openstack_name,
            },
        ],
    }
    s = Stack('inventory/group_vars/all/clouds.yml', d)
    s.set_public_key('infrastructure_key.pub')
    r = s.create_or_update()
    assert r['port'] == '22'
    assert 'ipv4' in r
    assert r == s.create_or_update()
    s.delete()


#
# Heat
#
@pytest.mark.skipif('SKIP_OPENSTACK_INTEGRATION_TESTS' in os.environ,
                    reason='skip integration test')
def test_heat_is_working(tmpdir):
    o = OpenStack('inventory/group_vars/all/clouds.yml')
    assert o.generate_clouds(tmpdir)
    heat_paths = []
    for f in sorted(os.listdir(tmpdir)):
        path = f'{tmpdir}/{f}'
        if Heat(path).is_working():
            heat_paths.append(path)
    heat_regions = []
    for path in heat_paths:
        config = yaml.load(open(path))
        heat_regions.append(config['clouds']['ovh']['region_name'])
    assert heat_regions == ['GRA5', 'SBG5']


def test_heat_definition():
    definitions = Heat.get_stack_definitions()
    assert 'bind-host' in definitions
    definition = Heat.get_stack_definition('bind-host')
    assert definition['name'] == 'bind-host'


def test_create_test_subdomain_no_bind(mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('enough.common.openstack.Stack.list', return_value=[])
    h = Heat('inventory/group_vars/all/clouds.yml')
    assert h.create_test_subdomain('my.tld') is None


def test_create_test_subdomain_with_bind(tmpdir, mocker, requests_mock):
    mocker.patch('enough.settings.CONFIG_DIR', str(tmpdir))
    d = f'{tmpdir}/inventory/group_vars/all'
    os.makedirs(d)
    assert not os.path.exists(f'{d}/domain.yml')
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('enough.common.openstack.Stack.list', return_value=['bind-host'])
    mocker.patch('enough.common.openstack.Stack.set_public_key')
    mocker.patch('enough.common.openstack.Stack.create_or_update', return_value={
        'ipv4': '1.2.3.4',
    })
    mocker.patch('enough.common.openstack.Heat.get_stack_definition')
    requests_mock.post(requests_mock_module.ANY, status_code=201)
    h = Heat('inventory/group_vars/all/clouds.yml')
    with modified_environ(ENOUGH_API_TOKEN="TOKEN"):
        fqdn = h.create_test_subdomain('my.tld')
    assert '.test.my.tld' in fqdn
    assert os.path.exists(f'{d}/domain.yml')


#
# OpenStack
#
@pytest.mark.skipif('SKIP_OPENSTACK_INTEGRATION_TESTS' in os.environ,
                    reason='skip integration test')
def test_region_list():
    o = OpenStack('inventory/group_vars/all/clouds.yml')
    assert o.config['clouds']['ovh']['region_name'] in o.region_list()


@pytest.mark.skipif('SKIP_OPENSTACK_INTEGRATION_TESTS' in os.environ,
                    reason='skip integration test')
def test_region_empty(openstack_name):
    clouds_file = 'inventory/group_vars/all/clouds.yml'
    if OpenStack(clouds_file).region_empty():
        c = sh.openstack.bake('--os-cloud=ovh', _env={
            'OS_CLIENT_CONFIG_FILE': clouds_file,
        })
        c.image.create('--file=/dev/null', openstack_name)
    assert not OpenStack(clouds_file).region_empty()


def test_generate_clouds(tmpdir, mocker):
    o = OpenStack('tests/enough/common/data/common/openstack/clouds.yml')

    directory = f'{tmpdir}/hosting'

    mocker.patch.object(o, 'region_list', return_value=['REGION1', 'REGION2'])
    assert o.generate_clouds(directory)
    assert (sorted(os.listdir(directory)) ==
            ['08ff6631d2dcc143fd6dc985fb88c8b2', 'add942ac0f189e6a327066c40133072b'])

    # REGION2 is removed, REGION4 is added
    mocker.patch.object(o, 'region_list', return_value=['REGION1', 'REGION4'])
    assert o.generate_clouds(directory)
    assert (sorted(os.listdir(directory)) ==
            ['74fcb8559ecfa3c0a009996faf1536b3', 'add942ac0f189e6a327066c40133072b'])

    # no change
    assert o.generate_clouds(directory) is False

    os.link(f'{directory}/add942ac0f189e6a327066c40133072b', f'{tmpdir}/in-use')
    with pytest.raises(AssertionError) as e:
        mocker.patch.object(o, 'region_list', return_value=['REGION4'])
        o.generate_clouds(directory)
    assert 'has 2 links' in str(e)


def test_allocate_cloud(tmpdir, mocker):
    o = OpenStack('tests/enough/common/data/common/openstack/clouds.yml')

    mocker.patch('enough.common.openstack.OpenStack.region_list',
                 return_value=['REGION1', 'REGION2'])
    mocker.patch('enough.common.openstack.OpenStack.region_empty',
                 return_value=True)
    mocker.patch('enough.common.openstack.Heat.is_working',
                 return_value=True)

    directory = f'{tmpdir}/hosting'
    o.generate_clouds(directory)

    assert (o.allocate_cloud(directory, f'{tmpdir}/one') ==
            f'{directory}/08ff6631d2dcc143fd6dc985fb88c8b2')
    assert (o.allocate_cloud(directory, f'{tmpdir}/two') ==
            f'{directory}/add942ac0f189e6a327066c40133072b')
    assert o.allocate_cloud(directory, f'{tmpdir}/three') is False
