import json
import logging
import re
import sh
import tempfile
import textwrap

from enough import settings


def parse_output(output):
    json_result = re.sub(r'.*?=> ', '', output)
    return json.loads(json_result)


def bake_ansible_playbook():
    args = ['-i', 'inventory']
    if settings.CONFIG_DIR != '.':
        args.extend(['-i', f'{settings.CONFIG_DIR}/inventory'])
    logger = logging.getLogger(__name__)
    return sh.ansible_playbook.bake(
        *args,
        _tee=True,
        _out=lambda x: logger.info(x.strip()),
        _err=lambda x: logger.info(x.strip()),
        _truncate_exc=False,
        _cwd=settings.SHARE_DIR,
        _env={'ANSIBLE_NOCOLOR': 'true'},
    )


def get_variable(role, variable, host):
    with tempfile.NamedTemporaryFile() as f:
        # the sourrounding "> <" are to prevent conversion to int, list or whatever
        playbook = textwrap.dedent("""
        ---
        - hosts: all
          gather_facts: false

          roles:
            - role: "{{ rolevar }}"

          tasks:
            - name: print variable
              debug:
                msg: ">{{ variable }}<"
        """)
        f.write(bytearray(playbook, 'utf-8'))
        f.flush()
        print(playbook)
        r = bake_ansible_playbook()(
            '-e', f'rolevar={role}',
            '-e', 'variable={{ ' + variable + ' }}',
            '--limit', host,
            '--start-at-task=print variable',
            f.name)
        m = re.search(r'"msg": ">(.*)<"$', r.stdout.decode('utf-8'), re.MULTILINE)
        return m.group(1)
