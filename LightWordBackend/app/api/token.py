from flask import jsonify, g, request

from app.api import api
from app.models import User
from app.api.auth import basic_auth, token_auth


@api.route('/token', methods=['POST'])
@basic_auth.login_required
def get_token():
    expires = request.args.get('expires', default = 86400, type = int)
    g.user.last_login()

    return jsonify({'token': g.user.generate_jwt(expires),
                    'token_type': 'Bearer', 
                    'expires_in': expires})

@api.route('/token/refresh', methods=['GET'])
@token_auth.login_required
def refresh_token():
    expires = request.args.get('expires', default = 86400, type = int)
    g.user.last_login()

    return jsonify({'token': g.user.generate_jwt(expires),
                    'token_type': 'Bearer', 
                    'expires_in': expires})