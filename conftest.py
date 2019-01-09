# meant to be read by testinfra in molecule/*/tests
# when assuming molecule/*/molecule.yml sets PYTHONPATH=../..

from tests.icinga_helper import IcingaHelper


def pytest_configure(config):
    IcingaHelper.set_ansible_inventory(config.getoption("--ansible-inventory"))
