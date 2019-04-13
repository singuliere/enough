from django.http import JsonResponse
from rest_framework.decorators import api_view
from io import StringIO
import sh
from enough import configuration
import re
import json


def run_ansible(*args, **kwargs):
    out = StringIO()
    kwargs['_out'] = out
    sh.ansible(*args, **kwargs)
    return out.getvalue()


@api_view(['POST'])
def bind(request):
    confdir = configuration.get_directory(None)
    bind_host = request.data.get('bind_host', 'bind-host')
    args = ['server=localhost']
    for k in ('zone', 'record', 'ttl', 'type', 'value'):
        if k in request.data:
            args.append(f'{k}={request.data[k]}')
    r = run_ansible('-i', f'{bind_host},',
                    '--private-key', f'{confdir}/id_rsa',
                    '--user=debian',
                    bind_host,
                    '--one-line',
                    f'--playbook-dir={confdir}',
                    '-m', 'nsupdate', '-a', " ".join(args),
                    _env={
                        'ANSIBLE_NOCOLOR': 'true',
                        'ANSIBLE_HOST_KEY_CHECKING': 'False',
                    })
    json_result = re.sub(r'.*?=> ', '', r)
    print(json_result)
    result = json.loads(json_result)

    return JsonResponse({"out": result}, status=201)
