* git submodule update --init
* apt-get install virtualenv
* deactivate || true ; source bootstrap
* # get OpenStack credentials and store then in openrc.sh
* source openrc.sh
* openstack server list # should successfully return nothing on a new tenant
* cp clouds.yml.example clouds.yml
* # copy/paste the variable names from openrc.sh into clouds.yml
* molecule create -s icinga # create the virtual machine
* openstack server list # should successfully return nothing on a new tenant
* ansible-playbook --private-key id_rsa --user debian  -i openstack.py molecule/icinga/playbook.yml # installs icinga
* molecule converge -s icinga # identical to the above ansible-playbook
* molecule login -s icinga --host icinga-host # should ssh to the machine
* molecule destroy -s icinga # destroy the virtual machine and cleanup the tenant

----------------------------------------------------------------------

* molecule create -s weblate
* openstack.py --list # fill the cache
* USE_CACHE=true ansible-playbook --private-key id_rsa --user debian -i openstack.py securedrop-club-playbook.yml

----------------------------------------------------------------------

Testing strategy to verify we can go from nothing to the most recent
version and also upgrade from the currently used version to the most
recent version. Assuming we always tag the repository before applying
it to the production.

Using an empty tenant:

git checkout previous-version-tag
molecule verify # nothing -> previous-version-tag
git checkout master # version under test
molecule verify # previous-version-tag -> master
molecule tests # nothing -> master
