from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.utils import json

from favorite.models import Favorite
from post.models import Post


class FavoriteCreateListTestCase(APITestCase):
    url = reverse("favorite:list-create")
    url_token_login = reverse("token_obtain_pair")

    def setUp(self):
        # Istifadeci yaradiriq
        self.username = "test_user"
        self.password = "test123456"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.post = Post.objects.create(title="Title", content="Test Content")
        self.test_jwt_authentication()

    def test_jwt_authentication(self):
        # Istifadecini token ile sisteme daxil edirik
        response = self.client.post(self.url_token_login, data={"username": self.username, "password": self.password})
        self.assertEqual(200, response.status_code)
        self.access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_add_favourite(self):
        # Postu duzgun formada yaradiriq
        self.data = {
            "content": "test_content",
            "user": self.user.id,
            "post": self.post.id
        }
        response = self.client.post(self.url, self.data)
        self.assertEqual(201, response.status_code)

    def test_add_favourite_twice(self):
        # Postu arxa arxaya favourite edilse error versin
        self.test_add_favourite()
        response = self.client.post(self.url, self.data)
        self.assertEqual(400, response.status_code)

    def test_list_all_favourite(self):
        # Butun fav postlari duz
        self.test_add_favourite()
        response = self.client.get(self.url)
        self.assertTrue(len(json.loads(response.content)["results"]) == Favorite.objects.filter(user=self.user).count())


class FavoriteUpdateDeleteTestCase(APITestCase):
    login_url = reverse("token_obtain_pair")

    def setUp(self):
        # Istifadeci yaradiriq
        self.username = "test_user"
        self.password = "test123456"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user2 = User.objects.create_user(username="test_user2", password="test123456")
        self.post = Post.objects.create(title="Title", content="Test Content")
        self.favourite = Favorite.objects.create(user=self.user, post=self.post)
        self.detail_url = reverse("favorite:update-delete", kwargs={"pk": self.favourite.pk})
        self.test_jwt_authentication()

    def test_jwt_authentication(self, username="test_user", password="test123456"):
        # Istifadecini token ile sisteme daxil edirik
        response = self.client.post(self.login_url, data={"username": username, "password": password})
        self.assertEqual(200, response.status_code)
        self.access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_fav_delete(self):
        # Oz favorite -ni silmek
        response = self.client.delete(self.detail_url)
        self.assertEqual(204, response.status_code)

    def test_fav_delete_different_user(self):
        # Bashqasinin favorite -ni sile bilmemek
        self.test_jwt_authentication(self.user2.username)
        response = self.client.delete(self.detail_url)
        self.assertEqual(403, response.status_code)

    def test_fav_update(self):
        # Oz favorite -nin kontentini yenilemek
        data = {"content": "test_content"}
        response = self.client.put(self.detail_url, data=data)
        self.assertEqual(200, response.status_code)
        self.assertTrue(Favorite.objects.get(pk=self.favourite.pk).content == data["content"])

    def test_not_your_fav_update(self):
        # Bashqasinin favorite -nin kontentini yenileye bilmemek
        self.test_jwt_authentication(self.user2.username)
        data = {"content": "test_content"}
        response = self.client.put(self.detail_url, data=data)
        self.assertEqual(403, response.status_code)

    def test_not_show_fav_update(self):
        # Sistemden cixish etmish istifadeci seifeni gormesin
        self.client.credentials()
        response = self.client.get(self.detail_url)
        self.assertEqual(401, response.status_code)