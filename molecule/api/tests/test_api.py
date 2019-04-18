import requests
import yaml
import dns.resolver
import gitlab_utils
from bs4 import BeautifulSoup

testinfra_hosts = ['api-host']


def get_domain():
    vars_dir = '../../inventories/common/group_vars/all'
    return yaml.load(open(vars_dir + '/domain.yml'))['domain']


def api_sign_in(host):
    domain = get_domain()

    #
    # GitLab home page
    #
    lab = requests.Session()
    lab.verify = '../../certs'
    lab_url = f'https://lab.{domain}'
    r = lab.get(lab_url + '/users/sign_in')
    soup = BeautifulSoup(r.text, 'html.parser')
    authenticity_token = soup.select(
        'form[action="/users/sign_in"] input[name="authenticity_token"]')[0]['value']
    r.raise_for_status()

    #
    # GitLab Login
    #
    r = lab.post(lab_url + '/users/sign_in', data={
        'authenticity_token': authenticity_token,
        'user[login]': 'root',
        'user[password]': gitlab_utils.get_password(),
        'user[remember_me]': 0,
    })
    r.raise_for_status()

    #
    # API login
    #
    api = requests.Session()
    api.verify = '../../certs'
    api.url = f'https://api.{domain}'
    r = api.get(api.url + '/accounts/gitlab/login/?process=login', allow_redirects=False)
    # print(r.headers['Location'])
    assert 'oauth/authorize' in r.headers['Location']
    r.raise_for_status()

    #
    # GitLab OAuth confirmation page
    #
    r = lab.get(r.headers['Location'])
    r.raise_for_status()
    assert 'An error' not in r.text
    soup = BeautifulSoup(r.text, 'html.parser')
    data = {
        'commit': 'Authorize',
    }
    for input in soup.select('form[action="/oauth/authorize"]:nth-child(2) input[type="hidden"]'):
        if input.get('name') is None or input.get('value') is None:
            continue
        data[input['name']] = input['value']
    #  print(str(data))
    #  print(soup.prettify())
    r = lab.post(lab_url + '/oauth/authorize', data=data, allow_redirects=False)
    r.raise_for_status()
    assert 'accounts/gitlab/login/callback' in r.headers['Location']

    # print(r.headers['Location'])
    r = api.get(r.headers['Location'], allow_redirects=False)
    # print(r.headers['Location'])
    r.raise_for_status()
    if '/accounts/social/signup/' == r.headers['Location']:
        #
        # API confirm email
        #
        r = api.get(f"{api.url}{r.headers['Location']}")
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        data = {}
        for input in soup.select('form input'):
            if input.get('name') is None or input.get('value') is None:
                continue
            data[input['name']] = input['value']
        # print(str(data))
        # print(soup.prettify())
        r = api.post(f'{api.url}/accounts/social/signup/', data=data, allow_redirects=False)
        r.raise_for_status()

    assert r.headers['Location'] == '/member/'

    #
    # API member page
    #
    r = api.get(f"{api.url}{r.headers['Location']}")
    r.raise_for_status()
    #
    # Get rest-framework token
    #
    soup = BeautifulSoup(r.content, 'html.parser')
    # print(soup.prettify())
    element = soup.select('#token')
    assert len(element) == 1
    token = element[0].contents[0]
    assert len(token) == 40
    return token


#
# debug with
#
# molecule login -s api --host=api-host
# docker exec -ti tmp_enough-enough_1 journalctl -f --unit enough
#
def test_add_host(host):
    token = api_sign_in(host)
    domain = get_domain()
    url = f"https://api.{domain}"
    s = requests.Session()
    s.headers = {'Authorization': f'Token {token}'}
    s.verify = '../../certs'
    data = {
        "zone": domain,
        "record": f"foo.{domain}.",
        "ttl": "1800",
        "type": "A",
        "value": "1.2.3.4",
    }
    r = s.post(f'{url}/bind/', json=data, timeout=5)
    # print(r.text)
    r.raise_for_status()
    resolver = dns.resolver.Resolver()
    bind_ip = str(resolver.query(f'bind.{domain}.')[0])
    resolver.nameservers = [bind_ip]
    assert '1.2.3.4' == str(resolver.query(f'foo.{domain}.', 'a')[0])
