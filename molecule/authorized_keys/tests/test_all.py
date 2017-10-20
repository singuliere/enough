import os
import subprocess
import pytest
import yaml

def test_all(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['authorized_keys_host']['ansible_host']
    marker = "MARKER"
    output = subprocess.check_output(
        "ssh -i roles/authorized_keys/files/test_keys/testkey "
        "debian@" + address + " echo " + marker,
        stderr=subprocess.STDOUT,
        shell=True)
    assert marker in output.strip()
