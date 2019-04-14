from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create an API user'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('email')
        parser.add_argument('password')

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if User.objects.filter(username=kwargs['username']):
            print('Already exists ' + str(User.objects.filter(username=kwargs['username'])))
        else:
            User.objects.create_superuser(kwargs['username'], kwargs['email'], kwargs['password'])
            print('Created')
