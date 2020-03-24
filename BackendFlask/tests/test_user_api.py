import unittest
import json
from requests.auth import _basic_auth_str
from tests import TestConfig
from app import create_app, db
from app.models import User, UserConfig

class UserAPITestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_create(self):
        response = self.client.post('/user',
        json = {
            "username": "test",
            "usermail": "test@test.com",
            "password": "123456"
        })

        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(json_response.get('token'))

        #重复注册测试
        response = self.client.post('/user',
        json = {
            "username": "test",
            "usermail": "test@test.com",
            "password": "123456"
        })

        self.assertEqual(response.status_code, 400)

        #错误数据测试
        response = self.client.post('/user',
        json = {
            "username": "",
            "usermail": "test",
            "password": ""
        })

        self.assertEqual(response.status_code, 400)

        return {
            'Authorization': 'Bearer %s' % json_response['token'],
            'Content-Type': 'application/json'
        }
    
    def test_user_statistic(self):
        headers = self.test_user_create()

        response = self.client.get(
            '/user/statistic?days=10',
            headers = headers)

        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)

    def test_user_config(self):
        headers = self.test_user_create()

        response = self.client.get(
            '/user/config',
            headers = headers)

        data = response.get_data(as_text=True)
        self.assertIn('vtype', data)
        self.assertEqual(response.status_code, 200)

    def test_put_user_config(self):
        headers = self.test_user_create()

        response = self.client.put(
            '/user/config',
            json = {
                "timestamp":{
                        "M1": 5,
                        "M2": 20,
                        "M3": 720,
                        "M4": 1440,
                        "M5": 2880,
                        "M6": 5760,
                        "M7": 10080,
                        "M8": 14436,
                        "M9": 46080,
                        "M10": 92160
                },
                "vtype": 1,
                "target": 50,
                "order": 1,
                "pronounce": 1
            },
            headers = headers)

        data = response.get_data(as_text=True)
        self.assertIn('vtype', data)
        self.assertEqual(response.status_code, 200)

    def test_user_profile(self):
        headers = self.test_user_create()

        response = self.client.get(
            '/user/profile',
            headers = headers)

        data = response.get_data(as_text=True)
        self.assertIn('username', data)
        self.assertEqual(response.status_code, 200)

    def test_user_word(self):
        headers = self.test_user_create()

        response = self.client.get(
            '/user/word',
            headers = headers)

        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)