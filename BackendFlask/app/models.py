#--*-- coding:utf-8 --*--
import os, jwt, random, re, json

from flask import current_app
from datetime import datetime, timedelta, date
from passlib.apps import custom_app_context as pwd_hash
from sqlalchemy import func, desc, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import load_only
from sqlalchemy.sql.expression import cast

from app import db

INITIAL_DATE = datetime(1970, 1, 1, 1, 1, 1)

class Vocabulary(db.Model):

    __tablename__ = 'vocabulary'
    __table_args__ = (db.UniqueConstraint('word', name='uix_word'), )

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(String(64), nullable=False, index=True)
    frequency = Column(Integer, default=99999, nullable=False)
    localdict = Column(Text(), nullable=False)

class VocabType(db.Model):

    __tablename__ = 'vocabtype'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vocabtype = Column(String(64), default='Default', nullable=False, index=True)
    alias = Column(String(32), default='Null', nullable=False)
    amount = Column(Integer, default=0, nullable=False)

    def to_dict(self):
        return {
                "id": self.id,
                "vocabtype": self.vocabtype,
                "alias": self.alias,
                "amount": self.amount
                }

    @classmethod
    def vtype_insert(cls, data: dict):
        tid = cls.query.filter_by(vocabtype = data['vocabtype']).first()
        if tid:
            return tid.id
        else:
            n = cls(**data)
            db.session.add(n)
            db.session.flush()
            return n.id

class VocabData(db.Model):

    __tablename__ = 'vocabdata'

    id = Column(Integer, primary_key=True, autoincrement=True)
    word_id = Column(Integer, ForeignKey(Vocabulary.id, ondelete='CASCADE'), nullable=False, index=True)
    vtype_id = Column(Integer, ForeignKey(VocabType.id, ondelete='CASCADE'), nullable=False, index=True)
    frequency = Column(Integer, default=99999, nullable=False)
    total_correct = Column(Integer, default=0, nullable=False)
    total_error = Column(Integer, default=0, nullable=False)
    
    vocabulary = db.relationship(Vocabulary, 
                            backref = db.backref('vdata', lazy='dynamic'),
                            cascade='all, delete')

    vtype = db.relationship(VocabType, 
                            backref = db.backref('vdata', lazy='dynamic'),
                            cascade='all, delete')

    def statistics(self, sta: bool):
        '''
        sta(True) or sta(False)
        '''
        if sta:
            self.total_correct += 1
        else:
            self.total_error += 1
        db.session.add(self)

    @classmethod
    def new_word(cls, uid: int, tid: int, n = 5, order = 0):
        #连表子查询User表不存在的Word
        if order == 1:
            orderby = cls.frequency
        else:
            orderby = func.rand() if db.session.bind.dialect.name == 'mysql' else func.random()

        userword =  UserData \
                    .query \
                    .options(load_only(UserData.word_id)) \
                    .filter_by(user_id = uid, vtype_id = tid) \
                    .subquery()
        return  cls \
                .query \
                .options(load_only(cls.word_id)) \
                .outerjoin(userword, cls.word_id == userword.c.word_id) \
                .filter(userword.c.word_id == None, cls.vtype_id == tid) \
                .order_by(orderby) \
                .limit(n)

class User(db.Model):

    __tablename__ = 'user'

    uid = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), index=True, unique=True)
    usermail = Column(String(64), index=True, unique=True)
    password_hash = Column(String(128))
    confirmed = Column(Boolean, default=False)
    create_time = Column(DateTime(), default=datetime.utcnow)
    last_login_time = Column(DateTime(), default=INITIAL_DATE)

    def to_dict(self):
        return {
            'uid': self.uid,
            'username': self.username,
            'usermail': self.usermail
        }

    def hash_password(self, password: str):
        self.password_hash = pwd_hash.hash(password)

    def verify_password(self, password: str):
        return pwd_hash.verify(password, self.password_hash)
    
    def last_login(self):
        self.last_login_time = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def generate_jwt(self, expiration = 3600):
        now = datetime.utcnow()
        payload = {
            'uid': self.uid,
            'exp': now + timedelta(seconds=expiration),
            'iat': now  
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')
    
    @staticmethod
    def verify_jwt(token: str):
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256'])
        except (jwt.exceptions.ExpiredSignatureError,
                jwt.exceptions.InvalidSignatureError,
                jwt.exceptions.DecodeError):
            return None
        return User.query.get(payload.get('uid')) 

class UserData(db.Model):

    __tablename__ = 'userdata'

    id = Column(Integer, primary_key=True, autoincrement=True)
    word_id = Column(Integer, ForeignKey(Vocabulary.id, ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey(User.uid, ondelete='CASCADE'), nullable=False, index=True)
    vtype_id = Column(Integer, ForeignKey(VocabType.id, ondelete='CASCADE'), nullable=False, index=True)
    timestamp = Column(DateTime(), default=datetime.utcnow, nullable=False)
    last_practice = Column(DateTime(), default=datetime.utcnow, nullable=False)
    stage = Column(Integer, default=1, nullable=False)
    correct = Column(Integer, default=1, nullable=False)
    wrong = Column(Integer, default=0, nullable=False)

    vocabulary = db.relationship( Vocabulary, 
                            backref = db.backref('userdata', lazy='dynamic'),
                            cascade='all, delete')
    user = db.relationship( User, 
                            backref = db.backref('userdata', lazy='dynamic'),
                            cascade='all, delete')
    vtype = db.relationship( VocabType, 
                            backref = db.backref('userdata', lazy='dynamic'),
                            cascade='all, delete')
    
    forget_time = { "M1": 5, 
        "M2": 20, "M3": 720, "M4": 1440, 
        "M5": 2880, "M6": 5760, "M7": 10080, 
        "M8": 14436, "M9": 46080, "M10": 92160 }

    def _caldate(self, minus = False):
        stage = len(self.forget_time)
        now = datetime.utcnow()
        datelist = [ obj for obj in self.forget_time.items() ]
        if self.stage < stage:
            #计算UTC时间+/-天数(分钟换算)
            minus_stage = 2 if minus and self.stage > 1 else 0
            self.timestamp = now + timedelta(minutes=datelist[self.stage - minus_stage][1])
        return self.timestamp

    @classmethod
    def remember(cls, wid: int, uid: int, tid: int):
        datadict = {
            'word_id': wid, 
            'user_id': uid, 
            'vtype_id': tid
        }
        dataobj = cls.query.filter_by(**datadict).first()
        if dataobj:
            if dataobj.stage < len(cls.forget_time):
                dataobj.timestamp = dataobj._caldate()
                dataobj.stage += 1
            dataobj.last_practice = datetime.utcnow()
            dataobj.correct += 1
            db.session.commit()
        else:
            dataobj = cls(**datadict)
            db.session.add(dataobj)
            return True

    @classmethod
    def forget(cls, wid: int, uid: int, tid: int):
        datadict = {
            'word_id': wid, 
            'user_id': uid, 
            'vtype_id': tid
        }
        dataobj = cls.query.filter_by(**datadict).first()
        if dataobj:
            if dataobj.stage > 1:
                dataobj.timestamp = dataobj._caldate(True)
                dataobj.stage -= 1
            dataobj.last_practice = datetime.utcnow()
            dataobj.wrong += 1
            db.session.commit()
            return dataobj.id is not None

    @classmethod
    def remembered(cls, wid: int, uid: int, tid: int):
        #已完全记住，+10年
        datadict = {
            'word_id': wid, 
            'user_id': uid, 
            'vtype_id': tid
        }
        utcnow = datetime.utcnow()
        ten_years = utcnow + timedelta(minutes=5126400)
        dataobj = cls.query.filter_by(**datadict).first()
        if dataobj:
            if dataobj.stage < len(cls.forget_time):
                dataobj.stage = 10
            dataobj.timestamp = ten_years
            dataobj.last_practice = utcnow
            dataobj.correct += 1
            db.session.commit()
        else:
            dataobj = cls(**datadict)
            dataobj.timestamp = ten_years
            dataobj.last_practice = utcnow
            db.session.add(dataobj)
            db.session.flush()
            return True

    @classmethod
    def user_word(cls, uid: int, tid: int, n = 10):
        for word in cls.query.order_by(desc(cls.correct)).filter_by(
                                    user_id = uid,
                                    vtype_id = tid
                                ).limit(n):
            yield { 'word': word.vocabulary.word, 
                    'correct': word.correct, 
                    'wrong': word.wrong }

    @classmethod
    def user_word_count(cls, uid: int, tid: int):
        return  dict(zip(['count', 'correct', 'wrong'],
                cls.query \
                .with_entities(func.count(cls.word_id),
                                cast(func.sum(cls.correct), Integer),
                                cast(func.sum(cls.wrong), Integer)) \
                .filter_by(user_id = uid,
                            vtype_id = tid).first()))
 
    @classmethod
    def recent_days(cls, uid: int, tid: int, days = 7):
        daysago = datetime.utcnow().date() - timedelta(days = days)
        for v in cls.query \
                  .with_entities(func.date(cls.last_practice),
                                 func.count(cls.last_practice),
                                 cast(func.sum(cls.correct), Integer),
                                 cast(func.sum(cls.wrong), Integer)) \
                  .filter_by(user_id = uid,
                             vtype_id = tid) \
                  .filter(cls.last_practice >= daysago) \
                  .group_by(func.date(cls.last_practice)).all():
                  
            yield dict(zip(['day', 'count', 'correct', 'wrong'],
                           [ r.strftime('%m-%d') if isinstance(r, date) else r for r in v ]))

    @classmethod
    def review_word(cls, uid: int, tid: int, n = 10):
        #按timestamp排序查询需要最先复习的Word
        utcnow = datetime.utcnow()
        userword = cls.query.filter_by(user_id = uid, vtype_id = tid) \
                      .order_by(cls.timestamp) \
                      .limit(n)
        available_list = [ obj for obj in userword if obj.timestamp <= utcnow ]
        if len(available_list) >= n:
            return available_list

class UserConfig(db.Model):

    __tablename__ = 'userconfig'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.uid, ondelete='CASCADE'), index=True)
    target = Column(Integer, default=50)
    vtype = Column(Integer, default=1)
    order = Column(Integer, default=1) # 0 by random, 1 by frequency
    pronounce = Column(Integer, default=1)
    timestamp = Column(String(128), default=UserData.forget_time)

    user = db.relationship( User, 
                            backref = db.backref('userconfig', lazy= 'dynamic'),
                            cascade= 'all, delete')

    @classmethod
    def init_config(cls, uid: int):
        config = {
            'user_id': uid,
            'timestamp': json.dumps(UserData.forget_time, ensure_ascii=False)
        }
        insert = cls(**config)
        db.session.add(insert)
        return insert.user

    @classmethod
    def get_config(cls, uid: int):
        config = cls.query.filter_by(user_id = uid).first()
        return {
                "timestamp": config.timestamp,
                "pronounce": config.pronounce,
                "target": config.target,
                "vtype": config.vtype,
                "order": config.order
                }
  