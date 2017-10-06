* apt-get install virtualenv
* deactivate || true ; source bootstrap
* # get OpenStack credentials and store then in openrc.sh
* source openrc.sh
* openstack server list # should successfully return nothing on a new tenant
* cp clouds.yml.example clouds.yml
* # copy/paste the variable names from openrc.sh into clouds.yml
* molecule create -s icinga # create the virtual machine and install icinga
* openstack server list # should successfully return nothing on a new tenant
* molecule login -s icinga --host icinga_host # should ssh to the machine
* molecule destroy -s icinga # destroy the virtual machine and cleanup the tenant
