import unittest
import json
from requests.auth import _basic_auth_str
from tests import TestConfig
from app import create_app, db
from app.models import User, UserConfig

class AuthAPITestCase(unittest.TestCase):

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

    def test_get_token(self):
        user = User(username='test', usermail='test@test.com')
        user.hash_password('123456')
        db.session.add(user)
        db.session.flush()
        UserConfig.init_config(user.uid)
        db.session.commit()

        response = self.client.post('/token', headers = {
        'Authorization': _basic_auth_str('test', '654321'),
        })
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/token', headers = {
        'Authorization': _basic_auth_str('test@test.com', '123456'),
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/token', headers = {
        'Authorization': _basic_auth_str('test', '123456'),
        })
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))

        return {
            'Authorization': 'Bearer %s' % json_response['token'],
            'Content-Type': 'application/json'
        }

    def test_get_token_refresh(self):
        headers = self.test_get_token()

        response = self.client.get('/token/refresh', headers = headers)
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
