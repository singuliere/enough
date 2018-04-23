Demo
====

`demo.securedrop.club <http://demo.securedrop.club>`_ is installed on an Debian host with Docker, using the `development VM <https://docs.securedrop.org/en/latest/development/virtual_environments.html#development-vm>`_ provided by the SecureDrop project.

The configuration variables are set in `molecule/demo/demo-playbook.yml` and all the specific roles are defined in `molecule/demo/roles`.

The demo is installed in `/srv/securedrop/`

The demo is administrable from `demo-host` via scripts provided in `/srv/securedrop/*.sh`. They are periodically launched by a cronjob. It rebuilds the demo if needed, update the demo from upstream when possible, and reset the credential if changed.
