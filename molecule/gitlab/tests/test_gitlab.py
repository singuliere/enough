import urllib3
import requests
import yaml
import os
import time

testinfra_hosts = ['gitlab-host']


def get_address(host):
    inventory = yaml.load(open(host.backend.ansible_inventory))
    address = inventory['all']['hosts']['gitlab-host']['ansible_host']
    return address


def get_password():
    variables = yaml.load(open('roles/gitlab/defaults/main.yml'))
    return variables['gitlab_password']


def get_private_token(url):
    r = requests.post(url + '/session', data={
        'login': 'root',
        'password': get_password(),
    })
    r.raise_for_status()
    return r.json()['private_token']


def recreate_test_project(url, headers):
    r = requests.get(url + '/projects/root%2Ftestproject', headers=headers)
    if r.status_code == requests.codes.ok:
        r = requests.delete(url + '/projects/root%2Ftestproject',
                            headers=headers)
        r.raise_for_status()
    for _ in range(10):
        r = requests.post(url + '/projects', headers=headers, data={
            "name": "testproject",
            "visibility": "public",
        })
        time.sleep(5)
        if r.status_code == 201:
            break
        print(str(r.text))
    r.raise_for_status()


def test_ci_runner(host, tmpdir):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    address = get_address(host)
    url = 'http://' + address + '/api/v3'
    headers = {'PRIVATE-TOKEN': get_private_token(url)}
    recreate_test_project(url, headers)
    host.run("rm -f /tmp/SERVERS")
    os.system("""
    set -ex
    cd {directory}
    test -d testproject && exit 0
    mkdir testproject
    cd testproject
    git init
    (
     echo 'jobs:'
     echo '  script: openstack server list > /tmp/SERVERS 2>&1'
    ) > .gitlab-ci.yml
    git add .gitlab-ci.yml
    git commit -m 'test'
    git remote add origin http://root:{password}@{address}/root/testproject.git
    git push -u origin master
    """.format(password=get_password(),
               address=address,
               directory=str(tmpdir)))
    for _ in range(20):
        if (host.file('/tmp/SERVERS').exists and
                host.file('/tmp/SERVERS').contains('gitlab-host')):
            break
        time.sleep(5)
    print(host.file('/tmp/SERVERS').content)
    assert host.file('/tmp/SERVERS').contains('gitlab-host')
