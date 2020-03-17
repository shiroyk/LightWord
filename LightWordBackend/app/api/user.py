import re
from flask import jsonify, request, Response, abort, g, json
from app import db
from app.utils import ConfigCache
from app.api import api
from app.api.auth import token_auth
from app.models import User, UserData, UserConfig

@api.route('/user/profile', methods=['GET'])
@token_auth.login_required
def get_user():
    return jsonify(g.user.to_dict())

@api.route('/user/config', methods=['GET'])
@token_auth.login_required
def get_config():
    config = ConfigCache().get()
    return jsonify(config)

@api.route('/user/config', methods=['PUT'])
@token_auth.login_required
def put_config():
    configs = request.get_json()
    if not configs:
        return {'message': 'You must provide JSON data.'}, 400

    configlist = ['vtype','pronounce', 'target']
    notin = [ v for v in configs.keys() if v in configlist ]
    if len(notin) != len(configlist):
        return {'message': 'Please provide correct config.'}, 400

    ConfigCache().remove()
    try:
        timestamp = configs['timestamp']
        if timestamp:
            timestamp = json.dumps(timestamp, ensure_ascii=False,)
            configs.update({'timestamp': timestamp})
    except KeyError:
        pass
    userconfig = UserConfig.query.filter_by(user_id=g.user.uid).first()
    for key, value in configs.items():
        setattr(userconfig, key, value)
    db.session.commit()
    return jsonify(ConfigCache().get())

@api.route('/user/word', methods=['GET'])
@token_auth.login_required
def get_user_word():
    n = request.args.get('days', default = 20, type = int)
    userconfig = ConfigCache().get()
    wordlist = UserData.user_word(g.user.uid, userconfig['vtype'], n)
    return jsonify(list(wordlist))

@api.route('/user/statistic', methods=['GET'])
@token_auth.login_required
def get_user_statistic():
    days = request.args.get('days', default = 7, type = int)
    userconfig = ConfigCache().get()
    dayscount = UserData.recent_days(g.user.uid, userconfig['vtype'], days)
    return jsonify(list(dayscount))

@api.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return {'message': 'You must provide JSON data.'}, 400

    errors = []
    if not 'username' in data or not data.get('username', None).strip():
        errors.append('Please provide a valid username.')
    if not 'usermail' in data or not re.match(r'\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,}', data.get('usermail', None)):
        errors.append('Please specify a valid email address.')
    if not 'password' in data or not data.get('password', None).strip():
        errors.append('Please provide a valid password.')

    if  User.query.filter_by(
        username = data.get('username')
        ).first() or User.query.filter_by(
        usermail = data.get('usermail')
        ).first():
        errors.append('Username or Email address already exists')

    if errors:
        return {'message': errors}, 400
    

    user = User()
    user.username = data['username']
    user.usermail = data['usermail']

    user.hash_password(data['password'])
    db.session.add(user)
    db.session.flush()
    UserConfig.init_config(user.uid)
    return jsonify({'token': user.generate_jwt(7200),
                    'token_type': 'Bearer', 
                    'expires_in': 7200}), 201