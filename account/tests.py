from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.utils import json

from account.models import Profile


class UserRegistrationTestCase(APITestCase):
    url = reverse('account:register')
    url_token_login = reverse('token_obtain_pair')

    def setUp(self):
        self.data_test_user = {"username": "testuser", "password": "test123456"}

    def test_user_registration(self):
        # Duzgun melumatlar ile qeydiyyat
        response = self.client.post(self.url, self.data_test_user)
        self.assertEqual(201, response.status_code)

    def test_user_invalid_password(self):
        # Zeif shifre ile qeydiyyat
        self.data_test_user["password"] = "1111"
        response = self.client.post(self.url, self.data_test_user)
        self.assertEqual(400, response.status_code)

    def test_username_unique(self):
        # Istifadeci adi movcuddur
        self.test_user_registration()
        response = self.client.post(self.url, self.data_test_user)
        self.assertEqual(400, response.status_code)

    def test_userprofile_is_create(self):
        # Istifadeci qeydiyyatdan kecende profil acilir
        self.test_user_registration()
        self.assertTrue(Profile.objects.filter(pk=1).exists())

    def test_user_authenticated_registration(self):
        # Session ile daxil olubsa seifeni gormesin
        self.test_user_registration()
        self.client.login(username=self.data_test_user["username"], password=self.data_test_user["password"])
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_user_token_registration(self):
        # Token ile daxil olubsa seifeni gormesin
        self.test_user_registration()
        response = self.client.post(self.url_token_login, self.data_test_user)
        self.assertEqual(200, response.status_code)
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)


class UserLoginTestCase(APITestCase):
    url_token_login = reverse('token_obtain_pair')

    def setUp(self):
        # SetUp funksiyasi init kimidi hersheyden evvel bashlayir
        self.username = "test_user"
        self.password = "test123456"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_user_token(self):
        # Istifadeci token ile daxil olmaga calishir
        response = self.client.post(self.url_token_login, {"username": self.username, "password": self.password})
        self.assertEqual(200, response.status_code)
        self.assertTrue("access" in json.loads(response.content))

    def test_user_invalid_data(self):
        # Istifadeci yanlish melumatla daxil olmaga calishir
        self.username = "not_registered_user"
        response = self.client.post(self.url_token_login, {"username": self.username, "password": self.password})
        self.assertEqual(401, response.status_code)

    def test_user_empty_data(self):
        # Istifadeci melumat daxil etmeden daxil olmaga calishir
        self.username = ""
        self.password = ""
        response = self.client.post(self.url_token_login, {"username": self.username, "password": self.password})
        self.assertEqual(400, response.status_code)


class UserPasswordChangeTestCase(APITestCase):
    url_password_change = reverse("account:change-password")
    url_token_login = reverse('token_obtain_pair')

    def setUp(self):
        # SetUp funksiyasi init kimidi hersheyden evvel bashlayir
        self.username = "test_user"
        self.password = "test123456"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_user_token_login(self):
        # Istifadeci token ile daxil olmaga calishir
        response = self.client.post(self.url_token_login, {"username": self.username, "password": self.password})
        self.assertEqual(200, response.status_code)
        self.assertTrue("access" in json.loads(response.content))
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_user_is_authenticated(self):
        # Hesaba daxil olmadan bu seifeni acmaq istese
        response = self.client.get(self.url_password_change)
        self.assertEqual(401, response.status_code)

    def test_with_valid_information(self):
        # Dogru melumatlari daxil ederek shifre deyishmek
        self.test_user_token_login()
        password_data = {"old_password": self.password, "new_password": "new123456"}
        # Update zamani put() methodunu istifade edirik
        response = self.client.put(self.url_password_change, password_data)
        self.assertEqual(204, response.status_code)

    def test_with_invalid_information(self):
        # Yanlish melumatlari daxil ederek shifre deyishmek
        self.test_user_token_login()
        password_data = {"old_password": "test_wrong", "new_password": "new123456"}
        # Update zamani put() methodunu istifade edirik
        response = self.client.put(self.url_password_change, password_data)
        self.assertEqual(400, response.status_code)

    def test_with_empty_information(self):
        # Bosh melumatlari daxil ederek shifre deyishmek
        self.test_user_token_login()
        password_data = {"old_password": "", "new_password": ""}
        # Update zamani put() methodunu istifade edirik
        response = self.client.put(self.url_password_change, password_data)
        self.assertEqual(400, response.status_code)


class UserProfileUpdateTestCase(APITestCase):
    url_profile = reverse("account:me")
    url_token_login = reverse("token_obtain_pair")

    def setUp(self):
        # SetUp funksiyasi init kimidi hersheyden evvel bashlayir
        self.username = "test_user"
        self.password = "test123456"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_user_token_login(self):
        # Istifadeci token ile daxil olmaga calishir
        response = self.client.post(self.url_token_login, {"username": self.username, "password": self.password})
        self.assertEqual(200, response.status_code)
        self.assertTrue("access" in json.loads(response.content))
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_not_authenticated_profile(self):
        # Hesaba daxil olmadan profile girilse error versin
        response = self.client.get(self.url_profile)
        self.assertEqual(401, response.status_code)

    def test_with_empty_data_profile(self):
        # Bosh melumatlar daxil ederse olmasin
        self.test_user_token_login()
        required_data = {
            "username": "",
            "profile": {
                "bio": "",
                "social": ""
            }}
        response = self.client.put(self.url_profile, required_data, format('json'))
        self.assertEqual(400, response.status_code)

    def test_with_valid_data_profile(self):
        # Vacib melumatlar daxil ederse yenilesin
        self.test_user_token_login()
        required_data = {
            "pk": 1,
            "first_name": "",
            "last_name": "",
            "username": self.username,
            "profile": {
                "pk": 1,
                "bio": "my_bio",
                "social": "vkontakte"
            }}
        response = self.client.put(self.url_profile, required_data, format('json'))
        self.assertEqual(200, response.status_code)
        # Gonderilen ile gelen data eynidirse yoxlayiriq
        self.assertEqual(json.loads(response.content), required_data)
