import pytest

from django.core.management import call_command
from django.test import TestCase

import sys
from io import StringIO
from contextlib import contextmanager


@contextmanager
def capture(command, *args, **kwargs):
    out, sys.stdout = sys.stdout, StringIO()
    try:
        command(*args, **kwargs)
        sys.stdout.seek(0)
        yield sys.stdout.read()
    finally:
        sys.stdout = out


class ApiManageTest(TestCase):

    @pytest.mark.django_db
    def test_apiuser(self):
        with capture(call_command, 'apiuser', 'test', 'test@...', 'top_secret') as stdout:
            assert 'Created' in stdout

        with capture(call_command, 'apiuser', 'test', 'test@...', 'top_secret') as stdout:
            assert 'Already exists' in stdout
