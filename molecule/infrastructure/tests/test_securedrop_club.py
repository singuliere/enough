import pytest

def test_molecule(Command):
    c = Command("""
    source /srv/virtualenv/bin/activate
    which molecule
    """)
    assert c.rc == 0
