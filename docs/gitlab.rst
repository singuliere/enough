GitLab
======

`lab.securedrop.club <http://lab.securedrop.club/main/securedrop-club/tree/master/molecule/gitlab/roles/gitlab>`_ is installed `with docker <https://hub.docker.com/r/sameersbn/gitlab/>`_ with the `https-portal letsencrypt reverse proxy <https://github.com/WeblateOrg/docker/blob/master/docker-compose-https.yml>`_.

The configuration variables are set in `host_vars/gitlab-host.yml` at
the root of the repository. It can be copied from
`molecule/gitlab/roles/gitlab/defaults/main.yml`.

* `gitlab_password`: database password
* `gitlab_github_api_key` and `gitlab_github_app_secret`: for :doc:`GitHub OAuth <github>`
* `gitlab_github_app_secret`, `gitlab_secrets_otp_key_base` and `gitlab_secrets_secret_key_base`: unique keys that can be generated with `pwgen -Bsv1 64`

