Demo
====

`demo.securedrop.club <http://demo.securedrop.club>`_ is installed on an Ubuntu host with Vagrant (`using libvirt provider <http://dachary.org/?p=4158>`_), using the `development VM <https://docs.securedrop.org/en/latest/development/virtual_environments.html#development-vm>`_ provided by the SecureDrop project.

The configuration variables are set in `molecule/demo/demo-playbook.yml` and all the specific roles are defined in `molecule/demo/roles`.

The demo is installed in `/srv/securedrop/` and accessing the VM can done in this directory via `$ vagrant ssh`.

The demo is administrable from `demo-host` via scripts provided in `/usr/local/bin/`. `check-securedrop-demo.sh` is periodically launched by a cronjob. It rebuilds the demo if needed, update the demo from upstream when possible, and reset the credential if changed.
