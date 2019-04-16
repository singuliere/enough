import requests
import yaml
import dns.resolver
import re

testinfra_hosts = ['api-host']


def get_domain():
    vars_dir = '../../inventories/common/group_vars/all'
    return yaml.load(open(vars_dir + '/domain.yml'))['domain']


def get_token(host, domain):
    with host.sudo():
        r = host.run(f"enough --domain {domain} manage drf_create_token admin")
    print(str(r))
    return re.sub(r'Generated token (\w+) for user admin', r'\1', str(r.stdout))


#
# debug with
#
# molecule login -s api --host=api-host
# docker exec -ti tmp_enough-enough_1 journalctl -f --unit enough
#
def test_add_host(host):
    domain = get_domain()
    token = get_token(host, domain)
    url = f"https://api.{domain}"
    s = requests.Session()
    s.headers = {
        'Authorization': f'Token {token}',
    }
    s.verify = '../../certs'
    data = {
        "zone": domain,
        "record": f"foo.{domain}.",
        "ttl": "1800",
        "type": "A",
        "value": "1.2.3.4",
    }
    r = s.post(f'{url}/bind/', json=data, timeout=5)
    r.raise_for_status()
    resolver = dns.resolver.Resolver()
    bind_ip = str(resolver.query(f'bind.{domain}.')[0])
    resolver.nameservers = [bind_ip]
    assert '1.2.3.4' == str(resolver.query(f'foo.{domain}.', 'a')[0])
