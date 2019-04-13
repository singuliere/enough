from enough.internal.cmd import main
from enough.version import __version__


def test_enough_install_script(capsys):
    assert main(['--debug', 'install', '--script']) == 0
    out, err = capsys.readouterr()
    assert 'docker run' in out
    assert 'function()' not in out
    assert __version__ in out


def test_enough_install_script_no_version(capsys):
    assert main(['--debug', 'install', '--script', '--no-version']) == 0
    out, err = capsys.readouterr()
    assert 'docker run' in out
    assert 'function()' not in out
    assert __version__ not in out


def test_enough_install_function(capsys):
    assert main(['--debug', 'install']) == 0
    out, err = capsys.readouterr()
    assert 'docker run' in out
    assert 'function enough()' in out
    assert __version__ in out


def test_enough_install_function_no_version(capsys):
    assert main(['--debug', 'install', '--no-version']) == 0
    out, err = capsys.readouterr()
    assert 'docker run' in out
    assert 'function enough()' in out
    assert __version__ not in out


def test_enough_install_service(capsys):
    assert main(['--debug', 'install', '--service']) == 0
    out, err = capsys.readouterr()
    assert 'ExecStart' in out
