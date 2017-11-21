import requests
import pytest

testinfra_hosts = ['demo-host']

def get_box_address(host):
    cmd = host.run('''
    cd /srv/securedrop
    vagrant ssh-config development | awk '$1 == "HostName" {print $2}'
    ''')
    return cmd.stdout

def test_source (host):
    cmd = host.run('curl http://{}:8080'.format(get_box_address (host)))
    assert cmd.rc == 0
    assert 'Submit documents' in cmd.stdout

def test_journalist (host):
    cmd = host.run('curl http://{}:8081'.format(get_box_address (host)))
    assert cmd.rc == 0
    assert 'You should be redirected automatically to target URL' in cmd.stdout
