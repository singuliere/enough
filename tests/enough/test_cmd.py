from enough.cmd import main


def test_help(capsys, mocker):
    # do not tamper with logging streams to avoid
    # ValueError: I/O operation on closed file.
    mocker.patch('cliff.app.App.configure_logging')
    assert main(['create']) == 0
    out, err = capsys.readouterr()
    assert 'OK' in out
