import requests
import pytest
import yaml
import time

import demo_utils

testinfra_hosts = ['demo-host']

def get_demo_address(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['demo-host']['ansible_host']
    return address

def test_default (host):
    demo_utils.check_demo(host)
    s = requests.Session()
    r = s.get('http://{}'.format(get_demo_address (host)), timeout=5)
    r.raise_for_status()
    assert 'Welcome to the SecureDrop demo' in r.text

def test_source (host):
    demo_utils.check_demo(host)
    domain = host.run("hostname -d").stdout.strip()
    s = requests.Session()
    s.headers.update({'host': 'source.demo.{}'.format(domain)})
    r = s.get('http://{}'.format(get_demo_address (host)), timeout=5)
    r.raise_for_status()
    assert 'Submit documents' in r.text

def test_journalist (host):
    demo_utils.check_demo(host)
    domain = host.run("hostname -d").stdout.strip()
    s = requests.Session()
    s.headers.update({'host': 'journalist.demo.{}'.format(domain)})
    r = s.get('http://{}/login'.format(get_demo_address (host)), timeout=5)
    r.raise_for_status()
    assert 'Login to access the journalist interface' in r.text
