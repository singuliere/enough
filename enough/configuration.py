import os


def get_directory(domain):
    if domain:
        d = os.path.expanduser(f'~/.enough/{domain}')
    else:
        d = os.path.expanduser(f'~/.enough/default')
    if not os.path.exists(d):
        os.makedirs(d)
    return d
