.. _ids:

Intrusion Detection System
==========================

Wazuh
-----

The `Wazuh <http://wazuh.com/>`_ server/manager is installed on a
dedicated host and all other hosts run an agent. The roles used by the `wazuh playbook <https://lab.enough.community/main/infrastructure/tree/master/molecule/wazuh>`_ are
from a submodule including `a short lived fork
<https://lab.enough.community/singuliere/wazuh-ansible>`_ of the
`wazuh-ansible repository
<https://github.com/wazuh/wazuh-ansible>`_. All commits unique to the
fork must match a pull request so they are eventually merged.

Notifications
-------------

All notifications are sent to `ids@enough.community`.
