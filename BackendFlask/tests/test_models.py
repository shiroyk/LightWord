import unittest
import json
from requests.auth import _basic_auth_str
from tests import TestConfig
from app import create_app, db
from app.models import User, UserConfig, UserData, VocabType, Vocabulary, VocabData

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
                v = line.decode().split(',', 2)
                vocab = Vocabulary(word= v[0], frequency = v[1], localdict = v[2])
                db.session.add(vocab)
                db.session.flush()
                vdata = VocabData(word_id = vocab.id, vtype_id = vtype, frequency = vocab.frequency)
                db.session.add(vdata)

    def test_user(self):
        user = User(username='test', usermail='test@test.com')
        user.hash_password('123456')
        db.session.add(user)
        db.session.flush()
        UserConfig.init_config(user.uid)
        db.session.commit()
    
    def test_userdata(self):
        userdata = UserData.remember(1,1,1)
        self.assertEqual(userdata, True)
        userdata = UserData.remember(1,1,1)
        self.assertEqual(userdata, None)
        
        userdata = UserData.forget(1,1,1)
        self.assertEqual(userdata, True)
        userdata = UserData.forget(2,1,1)
        self.assertEqual(userdata, None)

        userdata = UserData.remembered(1,1,1)
        self.assertEqual(userdata, None)
        userdata = UserData.remembered(2,1,1)
        self.assertEqual(userdata, True)

        userword = len(list(UserData.user_word(1,1)))
        self.assertEqual(userword, 2)
        userword_count = len(UserData.user_word_count(1,1))
        self.assertEqual(userword_count, 3)
        recent_day = len(list(UserData.recent_days(1,1)))
        self.assertEqual(recent_day, 1)

        review = UserData.review_word(1,1)
        self.assertEqual(review, None)