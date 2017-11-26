import os
import yaml


def get_address(host):
    for vars_dir in ('group_vars/all', '../../inventory/group_vars/all'):
        with_https_path = vars_dir + '/with_https.yml'
        if os.path.exists(with_https_path):
            with_https = yaml.load(open(with_https_path))
            if with_https and with_https.get('with_https'):
                return 'https://' + host.backend.host + '.' + yaml.load(
                    open(vars_dir + '/domain.yml'))['domain']
    inventory = yaml.load(open(host.backend.ansible_inventory))
    return ('http://' +
            inventory['all']['hosts'][host.backend.host]['ansible_host'])
