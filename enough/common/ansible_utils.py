import sh
import json
import io
import re
import tempfile
import textwrap


def parse_output(output):
    json_result = re.sub(r'.*?=> ', '', output)
    return json.loads(json_result)


def get_variable(configuration_directory, role, variable, host):
    with tempfile.NamedTemporaryFile() as f:
        playbook = textwrap.dedent("""
        ---
        - hosts: all
          become: true
          gather_facts: false

          roles:
            - role: "{{ rolevar }}"

          tasks:
            - name: print variable
              debug:
                var: variable
        """)
        f.write(bytearray(playbook, 'utf-8'))
        f.flush()
        print(playbook)
        out = io.StringIO()
        sh.ansible_playbook('-e', f'rolevar={role}',
                            '-e', 'variable={{ ' + variable + ' }}',
                            '--limit', host,
                            '--start-at-task=print variable',
                            '-i', configuration_directory,
                            '-i', 'inventories/common',
                            f.name, _out=out, _env={'ANSIBLE_NOCOLOR': 'true'})
        m = re.search(r'"variable": "(.*)"$', out.getvalue(), re.MULTILINE)
        return m.group(1)
