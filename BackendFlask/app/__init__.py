from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

db = SQLAlchemy()
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
mail = Mail()

def create_app(config = None):
    app = Flask('LightWord')
    
    app.config.from_object(config)
    custom_header(app)
    custom_error(app)

    migrate = Migrate(app, db)
    migrate.init_app(app)

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    cache.init_app(app, config={"CACHE_TYPE":"redis"})
    db.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)

    from app.api import api
    
    app.register_blueprint(api, url_prefix='/api')

    return app

def custom_header(app):
    @app.after_request
    def add_header(response):
        response.headers['X-Api-Version'] = 'v1'
        return response

def custom_error(app):
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {
            "message": "Too many requests, %s" % e.description
        }, 429