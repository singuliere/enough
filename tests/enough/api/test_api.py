import pytest
from django.urls import reverse
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
import mock


UserModel = get_user_model()


class APIUserAPITestCase(APITestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username='test', email='test@...', password='top_secret')
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


class TestAPI(APIUserAPITestCase):
    @pytest.mark.django_db
    @mock.patch('enough.api.views.run_ansible')
    @mock.patch('enough.api.permissions.has_permission')
    def test_bind(self, has_permission, run_ansible):
        url = reverse('bind')
        run_ansible.return_value = '51.68.81.22 | SUCCESS => {"changed": false}'
        has_permission.return_value = True
        data = {
            "bind_host": "51.68.81.22",
            "zone": "gyztqojxhe3tinjrbi.test.enough.community",
            "record": "foo.gyztqojxhe3tinjrbi.test.enough.community.",
            "ttl": "1800",
            "type": "A",
            "value": "1.2.3.4",
        }

        response = self.client.post(url, data, format='json')

        assert has_permission.called
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['out'], {"changed": False})
