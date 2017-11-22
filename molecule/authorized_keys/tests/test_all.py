import os
import subprocess
import pytest
import yaml

def test_all(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['authorized-keys-host']['ansible_host']
    marker = "MARKER"
    output = subprocess.check_output(
        "ssh -i roles/authorized_keys/files/test_keys/testkey {}@{} echo {}".format(
            ansible_user, address, marker),
        stderr=subprocess.STDOUT,
        shell=True)
    assert marker in output.strip()
