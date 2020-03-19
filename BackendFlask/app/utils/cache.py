from flask import g
from datetime import datetime, timedelta
from app import cache
from app.models import UserConfig, VocabType

class Caching(object):
    def __init__(self, key):
        self.uid = g.user.uid
        self.key = key + str(self.uid)

    def get(self):
        return cache.get(self.key)

    def remove(self):
        return cache.delete(self.key)

class VocabTypeCache(Caching):
    def __init__(self):
        self.key = 'VocabType'

    def get(self):
        vtype = cache.get(self.key)
        if not vtype:
            vtype = [ obj.to_dict() for obj in VocabType.query.all() ]
            cache.set(self.key, vtype, timeout=43200)
        return vtype

class ConfigCache(Caching):
    def __init__(self):
        Caching.__init__(self, 'userconfig')

    def get(self):
        user_config = cache.get(self.key)
        if not user_config:
            user_config = UserConfig.get_config(self.uid)
            cache.set(self.key, user_config, timeout=10800)
        return user_config

class DailyStatisticCache(Caching):
    def __init__(self):
        Caching.__init__(self, 'user_statistic')
        self.tomorrow = datetime.utcnow().replace(hour=0, minute=0, second=0) + timedelta(days=1) - datetime.utcnow()

    def get(self):
        user_statistic = cache.get(self.key)
        if not user_statistic:
            user_statistic = {
                'added': 0,
                'wrong': 0,
            }
            cache.set(self.key, user_statistic, timeout=int(self.tomorrow.total_seconds()))
        return user_statistic
    
    def increase(self, key):
        user_statistic = self.get()
        if key == 1:
            user_statistic['added'] += 1
        elif key == 2:
            user_statistic['wrong'] += 1
        cache.set(self.key, user_statistic, timeout=int(self.tomorrow.total_seconds()))