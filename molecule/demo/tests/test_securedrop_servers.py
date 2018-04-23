import requests
import pytest
import time

import demo_utils

testinfra_hosts = ['demo-host']

def run_curl(host, port):
    demo_utils.check_demo(host)
    cmd = host.run('curl http://127.0.0.1:{port}'.format(port=port))
    assert cmd.rc == 0
    return cmd.stdout

def test_source(host):
    for port in ('8080', '9080'):
        out = run_curl(host, port)
        assert 'for the first time' in out
        assert '/?l=fr_FR' in out

def test_journalist(host):
    for port in ('8081', '9081'):
        out = run_curl(host, port)
        assert 'You should be redirected automatically to target URL' in out
