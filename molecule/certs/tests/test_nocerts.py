import urllib3
import re
import requests
import pytest
import yaml

testinfra_hosts = ['bind-host']

def test_certs(host):
    cmd = host.run("ls -l /etc/ssl/certs/fakele*")
    assert cmd.rc != 0
