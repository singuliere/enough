import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from bs4 import BeautifulSoup

UserModel = get_user_model()


class ListViewTest(TestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username='test', email='test@...', password='top_secret')

    @pytest.mark.django_db
    def test_view(self):
        self.client.login(username='test', password='top_secret')
        response = self.client.get(reverse('user_home'))
        soup = BeautifulSoup(response.content, 'html.parser')
        token = soup.select('#token')
        assert len(token) == 1
        assert len(token[0].contents[0]) == 40
        self.assertEqual(response.status_code, 200)
