import os

class Config(object):
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you can guess'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or 'shiroyk'
    FLASKY_ADMIN_MAIL = os.environ.get('FLASKY_ADMIN_MAIL') or 'kumoocat@gmail.com'

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 465)
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = os.environ.get('MAIL_SENDER')

    CACHE_REDIS_URL = RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://redis:6379/0'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://web:123456@db:3306/webdb?charset=utf8'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JSON_AS_ASCII = False
    BABEL_DEFAULT_LOCALE = 'zh_CN'
    UPLOAD_FOLDER = './static/upload'
    ALLOWED_EXTENSIONS = ['txt', 'text']

