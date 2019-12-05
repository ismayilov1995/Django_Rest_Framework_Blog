from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse

from comment.models import Comment
from post.models import Post


class CommentCreateUpdateTestCase(APITestCase):
    """
    # Bosh olmadigini yoxlayiriq her birinde
    1. Comment elave edirik
    2. Oz commentimi silirem
    3. Oz commentimi yenileyirem
    4. Basqasinin kommentini yenileye ve sile bilmemek
    5. Sistemde biri yoxdusa seife acilmasin
    """

    url_create = reverse("comment:create")
    url_token_login = reverse("token_obtain_pair")
    valid_data = True

    def setUp(self):
        self.username = "test_user"
        self.password = "test123456"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.user2 = User.objects.create_user(username="test_user2", password=self.password)
        self.post = Post.objects.create(title="Title", content="Test Content")
        self.test_jwt_authentication(self.username, self.password)

    # Istifadecini token ile sisteme daxil edirik
    def test_jwt_authentication(self, username="test_user", password="test123456"):
        response = self.client.post(self.url_token_login, data={"username": username, "password": password})
        self.assertEqual(200, response.status_code)
        self.access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    # Posta comment yaziriq ve bosh olmamasini yoxlayiriq
    def test_add_comment(self):
        self.comment_data = {"content": "test comment", "user": self.user.pk, "post": self.post.pk, "parent": ""}
        if self.valid_data:
            response = self.client.post(self.url_create, self.comment_data)
            self.url_detail = reverse("comment:update", kwargs={"pk": 1})
            self.assertEqual(201, response.status_code)
            self.valid_data = False
        if not self.valid_data:
            self.comment_data["content"] = ""
            response = self.client.post(self.url_create, self.comment_data)
            self.url_detail = reverse("comment:update", kwargs={"pk": 1})
            self.assertEqual(400, response.status_code)
            self.valid_data = True

    # Oz commentini sil
    def test_delete_own_comment(self):
        self.test_add_comment()
        response = self.client.delete(self.url_detail)
        self.assertEqual(204, response.status_code)
        self.assertFalse(Comment.objects.filter(pk=1).exists())


    # Oz commentini yenileyirsen ve bosh olmamasini yoxlayirsan
    def test_update_own_comment(self):
        self.test_add_comment()
        if self.valid_data:
            response = self.client.put(self.url_detail, data={"content": "test update content"})
            self.assertEqual(200, response.status_code)
            self.valid_data = False
        if not self.valid_data:
            response = self.client.put(self.url_detail, data={"content": ""})
            self.assertEqual(400, response.status_code)
            self.valid_data = True

    # Bashqasinin commentini gormemek ve silmemek
    def test_update_not_own_comment(self):
        self.test_add_comment()
        self.test_jwt_authentication(self.user2.username, self.password)
        response = self.client.get(self.url_detail)
        self.assertEqual(403, response.status_code)
        response = self.client.delete(self.url_detail)
        self.assertEqual(403, response.status_code)

    # Sistemde girish olmadiqda acilmasin
    def test_not_authenticated_comment(self):
        self.test_add_comment()
        self.client.credentials()
        response = self.client.get(self.url_detail)
        self.assertEqual(401, response.status_code)

