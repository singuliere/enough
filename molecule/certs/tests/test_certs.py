import urllib3
import re
import requests
import pytest
import yaml

testinfra_hosts = ['debian-host']

def test_certs(host):
    cmd = host.run("curl -m 5 -I https://debian-host.$(hostname -d)")
    assert cmd.rc == 0
