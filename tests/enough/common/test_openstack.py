import os
import pytest
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


def test_generate_clouds(tmpdir, mocker):
    o = OpenStack('tests/enough/common/data/common/openstack/clouds.yml')

    directory = f'{tmpdir}/hosting'

    mocker.patch.object(o, 'region_list', return_value=['REGION1', 'REGION2'])
    assert o.generate_clouds(directory)
    assert (sorted(os.listdir(directory)) ==
            ['11012f8ce408470f65eacf6daf0c132b', '742fb1a63c9a3b034dfea05e5c671602'])

    # REGION2 is removed, REGION4 is added
    mocker.patch.object(o, 'region_list', return_value=['REGION1', 'REGION4'])
    assert o.generate_clouds(directory)
    assert (sorted(os.listdir(directory)) ==
            ['11012f8ce408470f65eacf6daf0c132b', 'e519b99d96c0a309ec29d1a9937f2009'])

    # no change
    assert o.generate_clouds(directory) is False

    os.link(f'{directory}/11012f8ce408470f65eacf6daf0c132b', f'{tmpdir}/in-use')
    with pytest.raises(AssertionError) as e:
        mocker.patch.object(o, 'region_list', return_value=['REGION4'])
        o.generate_clouds(directory)
    assert 'has 2 links' in str(e)


def test_allocate_cloud(tmpdir, mocker):
    o = OpenStack('tests/enough/common/data/common/openstack/clouds.yml')

    directory = f'{tmpdir}/hosting'

    mocker.patch.object(o, 'region_list', return_value=['REGION1', 'REGION2'])
    mocker.patch.object(o, 'region_empty', return_value=True)

    o.generate_clouds(directory)

    assert (o.allocate_cloud(directory, f'{tmpdir}/one') ==
            f'{directory}/11012f8ce408470f65eacf6daf0c132b')
    assert (o.allocate_cloud(directory, f'{tmpdir}/two') ==
            f'{directory}/742fb1a63c9a3b034dfea05e5c671602')
    assert o.allocate_cloud(directory, f'{tmpdir}/three') is False
