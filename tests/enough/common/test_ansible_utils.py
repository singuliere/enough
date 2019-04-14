from enough.common import ansible_utils
import json
import yaml


def test_parse_output():
    data = {"changed": False}
    output = '51.68.81.22 | SUCCESS => ' + json.dumps(data)
    assert ansible_utils.parse_output(output) == data


def test_get_variable():
    defaults = yaml.load(open('molecule/api/roles/api/defaults/main.yml'))
    variable = 'api_admin_password'
    value = ansible_utils.get_variable('inventories', 'api', variable, 'api-host')
    assert defaults[variable] == value
