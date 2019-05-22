import yaml

from enough import settings


def get_driver():
    vars_dir = f'{settings.CONFIG_DIR}/inventory/group_vars/all'
    return yaml.load(open(f'{vars_dir}/infrastructure.yml'))['infrastructure_driver']
