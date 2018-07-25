.. _postfix:

Postfix mail server
===================

Each VM installed via Ansible is able to send emails from the `enough.community`
domain.

Postfix mail relay
------------------

A mail relay based on Postfix is defined on the host `postfix-host`, via the
playbook `molecule/postfix/postfix-relay-playbook.yml`, based on the
`Postfix DebOps <https://github.com/debops/ansible-postfix>`_ role.

It is configured as an open relay using `smtps`. The relaying restrictions are
set in :ref:`firewall <firewall>` using OpenStack.

Postfix mail satellite
----------------------

A Postfix satellite is defined on each host (except for `postfix-host`),
via the playbook `molecule/postfix/postfix-client-playbook.yml`, based on the
`Postfix DebOps <https://github.com/debops/ansible-postfix>`_ role.
