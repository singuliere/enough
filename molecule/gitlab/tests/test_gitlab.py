import urllib3
import os
import testinfra
import time

import gitlab_utils

testinfra_hosts = ['gitlab-host']


def test_ci_runner(host, tmpdir):
    lab_host = host
    runner_host = testinfra.host.Host.get_host(
        'ansible://runner-host',
        ansible_inventory=host.backend.ansible_inventory)

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session = gitlab_utils.session(lab_host)
    gitlab_utils.recreate_test_project(session, 'root', 'testproject')
    runner_host.run("rm -f /tmp/*.out")
    os.system("""
    set -ex
    cd {directory}
    test -d testproject && exit 0
    mkdir testproject
    cd testproject
    git init
    (
     echo 'jobs:'
     echo '  script: env > /srv/OPENSTACK.out 2>&1 ; \
                     docker ps > /srv/DOCKER.out 2>&1'
    ) > .gitlab-ci.yml
    git add .gitlab-ci.yml
    git commit -m 'test'
    git config http.sslVerify false
    git remote add origin \
         https://root:{password}@{address}/root/testproject.git
    git push -u origin master
    """.format(password=gitlab_utils.get_password(),
               address=gitlab_utils.get_fqdn(lab_host),
               directory=str(tmpdir)))

    for (what, expected) in (('OPENSTACK', 'OS_TENANT_NAME'),
                             ('DOCKER', 'CONTAINER')):
        success = False
        for _ in range(40):
            if (runner_host.file('/srv/' + what + '.out').exists and
                    runner_host.file('/srv/' + what + '.out').contains(
                        expected)):
                success = True
                break
            time.sleep(5)
        assert success
