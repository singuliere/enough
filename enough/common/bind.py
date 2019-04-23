import json
from io import StringIO
import re
import sh

from django.conf import settings


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


def run_ansible(*args, **kwargs):
    out = StringIO()
    kwargs['_out'] = out
    sh.ansible(*args, **kwargs)
    return out.getvalue()


def nsupdate(data, state):
    basedir = settings.BASE_DIR
    bind_host = data.get('bind_host', 'bind-host')
    args = [
        'server=localhost',
        f'state={state}',
    ]
    for k in ('zone', 'record', 'ttl', 'type', 'value'):
        if k in data:
            args.append(f'{k}={data[k]}')
    r = run_ansible('-i', f'{bind_host},',
                    '--private-key', f'{basedir}/id_rsa',
                    '--user=debian',
                    bind_host,
                    '--one-line',
                    f'--playbook-dir={basedir}',
                    '-m', 'nsupdate', '-a', " ".join(args),
                    _env={
                        'ANSIBLE_NOCOLOR': 'true',
                        'ANSIBLE_HOST_KEY_CHECKING': 'False',
                    })
    json_result = re.sub(r'.*?=> ', '', r)
    print(json_result)
    return json.loads(json_result)