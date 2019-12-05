from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.utils import json

from post.models import Post


class PostCreateUpdateTestCase(APITestCase):
    """
    # Bosh olmadigini yoxlayiriq her birinde
    1. Post elave edirik
    2. Oz postumu silirem
    3. Oz Postumu yenileyirem
    4. Basqasinin postunu yenileye ve sile bilmemek
    5. Sistemde biri yoxdusa seife acilmasin
    5. Butun postlari siyahilayiram
    """

    url_list_create = reverse("post:list")
    url_token_login = reverse("token_obtain_pair")
    valid_data = True

    def setUp(self):
        self.username = "test_user"
        self.password = "test123456"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user2 = User.objects.create_user(username="test_user2", password=self.password)
        self.post_data = {"title": "title", "content": "content", "image": "", "modified_by": ""}
        self.post = Post.objects.create(title="title", content="content")
        self.url_post_update = reverse("post:update", kwargs={"slug": self.post.slug})
        self.url_post_delete = reverse("post:delete", kwargs={"slug": self.post.slug})
        self.test_jwt_authentication(self.username, self.password)

    # Istifadecini token ile sisteme daxil edirik
    def test_jwt_authentication(self, username="test_user", password="test123456"):
        response = self.client.post(self.url_token_login, data={"username": username, "password": password})
        self.assertEqual(200, response.status_code)
        self.access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    # Yeni yaradiriq ve bosh olmamasini yoxlayiriq
    def test_create_post(self):
        if self.valid_data:
            response = self.client.post(self.url_list_create, self.post_data)
            self.assertEqual(201, response.status_code)
            self.valid_data = False
        if not self.valid_data:
            self.post_data = {"title": "", "content": ""}
            response = self.client.post(self.url_list_create, self.post_data)
            self.assertEqual(400, response.status_code)
            self.valid_data = True

    # Butun postlari getir
    def test_post_list(self):
        response = self.client.get(self.url_list_create)
        self.assertTrue(len(json.loads(response.content)["results"]) == Post.objects.all().count())

    # Sistemde girish olmadiqda acilmasin
    def test_not_authenticated_post(self):
        self.test_create_post()
        self.client.credentials()
        response = self.client.get(self.url_post_update)
        self.assertEqual(401, response.status_code)
        response = self.client.get(reverse("post:delete", kwargs={"slug": self.post.slug}))
        self.assertEqual(401, response.status_code)

    # Oz postunu sil
    def test_delete_own_post(self):
        response = self.client.delete(self.url_post_delete)
        self.assertEqual(204, response.status_code)
        self.assertFalse(Post.objects.filter(slug=self.post.slug).exists())

    # Oz postunu yenileyirsen ve bosh olmamasini yoxlayirsan
    def test_update_own_post(self):
        if self.valid_data:
            response = self.client.put(self.url_post_update, data=self.post_data)
            self.assertEqual(200, response.status_code)
            self.valid_data = False
        if not self.valid_data:
            post = Post.objects.values('pk','slug').get(pk=self.post.pk)
            response = self.client.put(reverse("post:update", kwargs={"slug": post["slug"]}), data={"title": "", "content": ""})
            self.assertEqual(400, response.status_code)
            self.valid_data = True

    # Bashqasinin postunu gormemek ve silmemek
    def test_update_not_own_post(self):
        self.test_jwt_authentication(self.user2.username, self.password)
        self.post_data["content"] = "test new"
        response = self.client.get(self.url_post_update)
        self.assertEqual(403, response.status_code)
        response = self.client.put(self.url_post_update, self.post_data)
        self.assertEqual(403, response.status_code)
        self.assertFalse(Post.objects.get(pk=self.post.pk).content == self.post_data["content"])
        response = self.client.delete(self.url_post_delete)
        self.assertEqual(403, response.status_code)

