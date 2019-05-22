from icinga2api.client import Client
import re
from enough.common import retry
import urllib3
import yaml
import testinfra
from tests.infrastructure import get_driver

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class IcingaHelper(object):

    # set by ../conftest.py
    @staticmethod
    def set_ansible_inventory(inventory):
        IcingaHelper.inventory = inventory

    def get_auth(self):
        host = testinfra.get_host('ansible://icinga-host', ansible_inventory=self.inventory)
        with host.sudo():
            f = host.file("/etc/icinga2/conf.d/api-users.conf")
            return (
                re.search('ApiUser "(.*)"', f.content_string).group(1),
                re.search('password = "(.*)"', f.content_string).group(1)
            )

    def get_address(self):
        if get_driver() == 'openstack':
            vars_dir = '../../inventory/group_vars/all'
            return 'icinga.' + yaml.load(
                open(vars_dir + '/domain.yml'))['domain']
        else:
            host = testinfra.get_host('ansible://icinga-host', ansible_inventory=self.inventory)
            return host.ansible.get_variables()['ansible_host']

    def get_client(self):
        (user, password) = self.get_auth()
        client = Client(
            'https://{}:5665'.format(self.get_address()),
            user, password,
            ca_certificate=False,
            timeout=5
        )
        return client

    @retry.retry(AssertionError, tries=7)
    def wait_for_service(self, client, name):
        answer = client.objects.get('Service', name)
        assert int(answer['attrs']['state']) == 0
        return True

    def is_service_ok(self, name):
        #
        # force the check to reduce the waiting time
        #
        client = self.get_client()
        answer = client.actions.reschedule_check(
            'Service',
            'service.__name=="{}"'.format(name),
        )
        assert len(answer['results']) == 1
        assert int(answer['results'][0]['code']) == 200

        return self.wait_for_service(client, name)
