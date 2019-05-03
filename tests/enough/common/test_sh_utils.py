import logging
import pytest
import sh
from enough.common import sh_utils


def test_run_sh(capsys):
    logging.getLogger('sh').setLevel(logging.CRITICAL)
    r = sh_utils.run_sh(sh.Command('./tests/enough/common/bin/sh_utils_run_ok.sh'))
    expected = "stdout1\nstdout2\nstderr1\n"
    assert r == expected
    out, err = capsys.readouterr()
    assert out == expected
    assert err == ''


def test_run_sh_fail(capsys):
    logging.getLogger('sh').setLevel(logging.CRITICAL)
    with pytest.raises(sh.ErrorReturnCode_1):
        sh_utils.run_sh(sh.Command('./tests/enough/common/bin/sh_utils_run_fail.sh'))
    out, err = capsys.readouterr()
    expected = "stdout1\nstdout2\nstderr1\n"
    assert out == expected
    assert f'STDOUT:\n{expected}' in err


def test_run_sh_long(capsys):
    logging.getLogger('sh').setLevel(logging.CRITICAL)
    with pytest.raises(sh.ErrorReturnCode_1):
        sh_utils.run_sh(sh.Command('./tests/enough/common/bin/sh_utils_run_long_fail.sh'))
    out, err = capsys.readouterr()
    length = sh.ErrorReturnCode.truncate_cap + 100
    expected = 'a' * length
    assert expected in out
    assert f'STDOUT:\n{expected}' in err
