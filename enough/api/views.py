from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from enough.api.permissions import IsEnoughGroupMember
from io import StringIO
import sh
import re
import json


def run_ansible(*args, **kwargs):
    out = StringIO()
    kwargs['_out'] = out
    sh.ansible(*args, **kwargs)
    return out.getvalue()


@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated, IsEnoughGroupMember))
def bind(request):
    basedir = settings.BASE_DIR
    bind_host = request.data.get('bind_host', 'bind-host')
    args = ['server=localhost']
    for k in ('zone', 'record', 'ttl', 'type', 'value'):
        if k in request.data:
            args.append(f'{k}={request.data[k]}')
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
    result = json.loads(json_result)

    return JsonResponse({"out": result}, status=201)
