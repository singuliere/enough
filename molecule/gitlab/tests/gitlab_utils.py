import yaml


def get_fqdn():
    vars_dir = '../../inventory/group_vars/all'
    return 'lab.' + yaml.load(open(vars_dir + '/domain.yml'))['domain']


def get_url():
    return 'https://' + get_fqdn()


def get_password():
    variables = yaml.load(open(
        '../../inventory/group_vars/gitlab/gitlab.yml'))
    return variables['gitlab_password']
