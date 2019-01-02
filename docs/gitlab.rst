GitLab
======

`lab.enough.community <http://lab.enough.community/main/infrastructure/tree/master/molecule/gitlab/roles/gitlab>`_ is installed `with docker <https://hub.docker.com/r/sameersbn/gitlab/>`_.

The configuration variables are set in `inventories/common/host_vars/gitlab-host/gitlab.yml` at
the root of the repository. It can be copied from
`molecule/gitlab/roles/gitlab/defaults/main.yml`.

* `gitlab_password`: database password
* `gitlab_shared_runners_registration_token`: runner registration token predefined for tests
* `gitlab_secrets_db_key_base`, `gitlab_secrets_otp_key_base` and `gitlab_secrets_secret_key_base`: unique keys that can be generated with `pwgen -Bsv1 64`
* `gitlab_os_*`: default to the OpenStack tenant variables. In production they should be set to a dedicated tenant, entirely separated from production, because it will be used by all commits pushed to the repository.
