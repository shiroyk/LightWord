from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth

from app.models import User

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(user, password):
    user = User.get_uid(user)
    if not user:
        return False
    g.user = user
    return user.verify_password(password)

@basic_auth.error_handler
def basic_auth_error():
    return ({"message": "401 Unauthorized"}), 401

@token_auth.verify_token
def verify_token(token):
    g.user = User.verify_jwt(token)
    if g.user:
        g.user.last_login()
    return g.user is not None

@token_auth.error_handler
def token_auth_error():
    return ({"message": "401 Unauthorized"}), 401