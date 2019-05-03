import os

from enough.common.hosting import Hosting


def test_ensure_ssh_key(tmpdir):
    h = Hosting({'name': 'NAME'})
    h.config_dir = tmpdir
    h.ensure_ssh_key()
    assert os.path.exists(f'{tmpdir}/infrastructure_key.pub')
