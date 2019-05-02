import json
import re

from django.conf import settings

from enough.common import ansible_utils


def delegate_dns(zone, name, ip):
    results = []
    results.append(nsupdate({
        "zone": f"{zone}.",
        "record": f"ns-{name}.{zone}.",
        "ttl": "1800",
        "type": "A",
        "value": ip,
    }, state='present'))
    #
    # For NS records, "present" is not idempotent, but "absent" is
    # idempotent so make sure it is absent before adding it
    #
    results.append(nsupdate({
        "zone": f"{zone}.",
        "record": f"{name}.{zone}.",
        "ttl": "1800",
        "type": "NS",
        "value": f"ns-{name}.{zone}.",
    }, state='absent'))
    results.append(nsupdate({
        "zone": f"{zone}.",
        "record": f"{name}.{zone}.",
        "ttl": "1800",
        "type": "NS",
        "value": f"ns-{name}.{zone}.",
    }, state='present'))
    return results


def nsupdate(data, state):
    configdir = settings.CONFIG_DIR
    bind_host = data.get('bind_host', 'bind-host')
    args = [
        'server=localhost',
        f'state={state}',
    ]
    for k in ('zone', 'record', 'ttl', 'type', 'value'):
        if k in data:
            args.append(f'{k}={data[k]}')
    r = ansible_utils.run(
        'ansible',
        '-i', f'{bind_host},',
        '--private-key', f'{configdir}/infrastructure_key',
        '--user=debian',
        bind_host,
        '--one-line',
        f'--playbook-dir={configdir}',
        '-m', 'nsupdate', '-a', " ".join(args),
        _env={
            'ANSIBLE_NOCOLOR': 'true',
            'ANSIBLE_HOST_KEY_CHECKING': 'False',
        })
    json_result = re.sub(r'.*?=> ', '', r)
    print(json_result)
    return json.loads(json_result)
