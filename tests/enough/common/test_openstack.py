import os
import pytest
import yaml

from enough.common.openstack import OpenStack


@pytest.mark.skipif('SKIP_OPENSTACK_INTEGRATION_TESTS' in os.environ,
                    reason='skip integration test')
def test_region_list():
    o = OpenStack('inventories/common/group_vars/all/clouds.yml')
    assert o.config['clouds']['ovh']['region_name'] in o.region_list()


@pytest.mark.skipif('SKIP_OPENSTACK_INTEGRATION_TESTS' in os.environ,
                    reason='skip integration test')
def test_region_empty(openstack_client):
    clouds_file = 'inventories/common/group_vars/all/clouds.yml'
    if OpenStack.region_empty(clouds_file):
        openstack_client.image.create(
            '--property=enough=fixture', '--file=/dev/null', 'remove-me')
    assert not OpenStack.region_empty(clouds_file)


#
# Heat
#
@pytest.mark.skipif('SKIP_OPENSTACK_INTEGRATION_TESTS' in os.environ,
                    reason='skip integration test')
def test_heat_is_working(tmpdir):
    o = OpenStack('inventories/common/group_vars/all/clouds.yml')
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
