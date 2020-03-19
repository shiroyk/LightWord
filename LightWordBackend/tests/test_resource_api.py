import unittest
import json
from requests.auth import _basic_auth_str
from tests import TestConfig
from app import create_app, db
from app.models import User, UserConfig, VocabType, Vocabulary, VocabData

class ResourceAPITestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.vocabulary_data_init('tests/test.csv')
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def vocabulary_data_init(self, path):
        filename = path.split('/')[-1].split('.')[0]

        with open(path,'rb') as f:
            count = 0
            while True:
                data = f.read(65536)
                if not data: break
                count += data.count(b'\n')
        vtype = VocabType.vtype_insert({'vocabtype': filename, 'amount': count})

        with open(path,'rb') as f:
            for line in f:
                v = line.decode().split(',', 1)
                vocab = Vocabulary(word= v[0], localdict = v[1])
                db.session.add(vocab)
                db.session.flush()
                vdata = VocabData(word_id = vocab.id, vtype_id = vtype)
                db.session.add(vdata)

    def test_get_token(self):
        user = User(username='test', usermail='test@test.com')
        user.hash_password('123456')
        db.session.add(user)
        db.session.flush()
        UserConfig.init_config(user.uid)
        db.session.commit()

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

    def test_exercise(self):
        headers = self.test_get_token()

        response = self.client.get('/resource/exercise', headers = headers)
        data = response.get_data(as_text=True)
        self.assertIn('meaning', data)
        self.assertEqual(response.status_code, 200)

    def test_exercise_status(self):
        headers = self.test_get_token()

        response = self.client.put(
            '/resource/exercise/status',
            json = {
                "word": 99999,
                "vtype": 9,
                "status": 9
            },
            headers = headers)

        self.assertEqual(response.status_code, 400)

        response = self.client.put(
            '/resource/exercise/status',
            json = {
                "word": '',
                "vtype": '',
                "status": ''
            },
            headers = headers)

        self.assertEqual(response.status_code, 400)

        response1 = self.client.put(
            '/resource/exercise/status',
            json = {
                "word": 1,
                "vtype": 1,
                "status": 1
            },
            headers = headers)

        response2 = self.client.put(
            '/resource/exercise/status',
            json = {
                "word": 1,
                "vtype": 1,
                "status": 2
            },
            headers = headers)
        
        response3 = self.client.put(
            '/resource/exercise/status',
            json = {
                "word": 2,
                "vtype": 1,
                "status": 3
            },
            headers = headers)
        
        data = response1.get_data(as_text=True)
        self.assertIn('added', data)
        self.assertEqual(response1.status_code, 200)
        data = response2.get_data(as_text=True)
        self.assertIn('wrong', data)
        self.assertEqual(response2.status_code, 200)
        data = response3.get_data(as_text=True)
        self.assertIn('added', data)
        self.assertEqual(response2.status_code, 200)
    
    def test_get_vtype(self):
        headers = self.test_get_token()

        response = self.client.get(
            '/resource/type',
            headers = headers)

        data = response.get_data(as_text=True)
        self.assertIn('vocabtype', data)
        self.assertEqual(response.status_code, 200)

    def test_put_vtype(self):
        headers = self.test_get_token()

        response = self.client.put(
            '/resource/type',
            json = {
                "alias": "test",
                "id": 2
            },
            headers = headers)

        self.assertEqual(response.status_code, 400)

        response = self.client.put(
            '/resource/type',
            json = {
                "alias": "",
                "id": ""
            },
            headers = headers)
            
        self.assertEqual(response.status_code, 400)

        response = self.client.put(
            '/resource/type',
            json = {
                "alias": "test",
                "id": 1
            },
            headers = headers)

        data = response.get_data(as_text=True)
        self.assertIn('vocabtype', data)
        self.assertEqual(response.status_code, 200)