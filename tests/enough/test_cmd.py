from enough.cmd import main


def test_help(capsys):
    assert main(['create']) == 0
    out, err = capsys.readouterr()
    assert 'OK' in out
