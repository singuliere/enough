import requests
import pytest
import yaml
import time

testinfra_hosts = ['demo-host']

def get_demo_address(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['demo-host']['ansible_host']
    return address

def test_default (host):
    s = requests.Session()
    for _ in range (100):
        try:
            r = s.get('http://{}'.format(get_demo_address (host)), timeout=5)
            r.raise_for_status()
            break
        except:
            time.sleep(10)
    assert 'Welcome to the SecureDrop demo' in r.text

def test_source (host):
    domain = host.run("hostname -d").stdout.strip()
    s = requests.Session()
    for _ in range (100):
        try:
            s.headers.update({'host': 'source.demo.{}'.format(domain)})
            r = s.get('http://{}'.format(get_demo_address (host)), timeout=5)
            r.raise_for_status()
            break
        except:
            time.sleep(10)
    assert 'Submit documents' in r.text

def test_journalist (host):
    domain = host.run("hostname -d").stdout.strip()
    s = requests.Session()
    for _ in range (100):
        try:
            s.headers.update({'host': 'journalist.demo.{}'.format(domain)})
            r = s.get('http://{}'.format(get_demo_address (host)), timeout=5)
            r.raise_for_status()
            break
        except:
            time.sleep(10)
    assert 'Login to access the journalist interface' in r.text
