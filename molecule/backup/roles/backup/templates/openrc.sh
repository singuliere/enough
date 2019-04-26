#!/usr/bin/env bash
export OS_AUTH_URL={{ clouds.ovh.auth.auth_url }}
export OS_IDENTITY_API_VERSION=3
export OS_PROJECT_NAME={{ clouds.ovh.auth.project_name }}
export OS_PROJECT_ID={{ clouds.ovh.auth.project_id }}
export OS_USER_DOMAIN_NAME={{ clouds.ovh.auth.user_domain_name }}
export OS_USERNAME={{ clouds.ovh.auth.username }}
export OS_PASSWORD={{ clouds.ovh.auth.password }}
export OS_REGION_NAME={{ clouds.ovh.region_name }}
