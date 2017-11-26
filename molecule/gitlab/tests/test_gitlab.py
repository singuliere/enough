import urllib3
import os
import time

import gitlab_utils

testinfra_hosts = ['gitlab-host']


def test_ci_runner(host, tmpdir):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    (scheme, address) = gitlab_utils.get_address(host)
    url = scheme + '://' + address + '/api/v3'
    headers = {'PRIVATE-TOKEN': gitlab_utils.get_private_token(url)}
    gitlab_utils.recreate_test_project(url, headers, 'root', 'testproject')
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
     echo '  script: env > /srv/TEST 2>&1'
    ) > .gitlab-ci.yml
    git add .gitlab-ci.yml
    git commit -m 'test'
    git config http.sslVerify false
    git remote add origin \
         {scheme}://root:{password}@{address}/root/testproject.git
    git push -u origin master
    """.format(password=gitlab_utils.get_password(),
               address=address,
               directory=str(tmpdir),
               scheme=scheme))

    success = False
    for _ in range(40):
        if (host.file('/srv/TEST').exists and
                host.file('/srv/TEST').contains('OS_TENANT_NAME')):
            success = True
            break
        time.sleep(5)
    assert success
