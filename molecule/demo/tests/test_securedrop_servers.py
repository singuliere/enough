import requests
import pytest
import time

testinfra_hosts = ['demo-host']

def test_source (host):
    for _ in range (100):
        try:
            cmd = host.run('curl http://127.0.0.1:8080')
            if cmd.rc != 0:
                raise ValueError ('curl returned non null error code')
            break
        except:
            time.sleep(10)
    assert cmd.rc == 0
    assert 'Submit documents' in cmd.stdout
    assert '/?l=fr_FR' in cmd.stdout

def test_journalist (host):
    for _ in range (100):
        try:
            cmd = host.run('curl http://127.0.0.1:8081')
            if cmd.rc != 0:
                raise ValueError ('curl returned non null error code')
            break
        except:
            time.sleep(10)
    assert cmd.rc == 0
    assert 'You should be redirected automatically to target URL' in cmd.stdout
