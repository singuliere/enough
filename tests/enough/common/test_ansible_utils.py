from enough.common import ansible_utils
import json
import logging
import pytest
import yaml
import sh


def test_parse_output():
    data = {"changed": False}
    output = '51.68.81.22 | SUCCESS => ' + json.dumps(data)
    assert ansible_utils.parse_output(output) == data


def test_get_variable():
    defaults = yaml.load(open('molecule/api/roles/api/defaults/main.yml'))
    variable = 'api_admin_password'
    value = ansible_utils.get_variable('inventories', 'api', variable, 'api-host')
    assert defaults[variable] == value


def test_run(capsys):
    logging.getLogger('sh').setLevel(logging.CRITICAL)
    r = ansible_utils.run('./tests/enough/common/bin/ansible_utils_run_ok.sh')
    expected = "stdout1\nstdout2\nstderr1\n"
    assert r == expected
    out, err = capsys.readouterr()
    assert out == expected
    assert err == ''


def test_run_fail(capsys):
    logging.getLogger('sh').setLevel(logging.CRITICAL)
    with pytest.raises(sh.ErrorReturnCode_1):
        ansible_utils.run('./tests/enough/common/bin/ansible_utils_run_fail.sh')
    out, err = capsys.readouterr()
    expected = "stdout1\nstdout2\nstderr1\n"
    assert out == expected
    assert f'STDOUT:\n{expected}' in err


def test_run_long(capsys):
    logging.getLogger('sh').setLevel(logging.CRITICAL)
    with pytest.raises(sh.ErrorReturnCode_1):
        ansible_utils.run('./tests/enough/common/bin/ansible_utils_run_long_fail.sh')
    out, err = capsys.readouterr()
    length = sh.ErrorReturnCode.truncate_cap + 100
    expected = 'a' * length
    assert expected in out
    assert f'STDOUT:\n{expected}' in err
