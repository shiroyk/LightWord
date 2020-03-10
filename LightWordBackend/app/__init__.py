from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager,Shell
from flask_migrate import Migrate, MigrateCommand
from flask_caching import Cache


db = SQLAlchemy()
cache = Cache()


def create_app(config = None):
    app = Flask('DailyWord')
    
    app.config.from_object(config)
    custom_header(app)

    manager = Manager(app)
    migrate = Migrate(app, db)
    manager.add_command("db", MigrateCommand)

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    cache.init_app(app, config={"CACHE_TYPE":"redis"})
    db.init_app(app)

    from app.api import api
    
    app.register_blueprint(api, url_prefix='/')

    return app

def custom_header(app):
    @app.after_request
    def add_header(response):
        response.headers['X-Api-Version'] = 'v1'
        return response