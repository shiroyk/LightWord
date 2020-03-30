import re, random
from flask import jsonify, request, g, json, current_app
from app import db, limiter
from flask_mail import Message
from app.utils import ConfigCache, VerificationCode, send_email, generate_code
from app.api import api
from app.api.auth import token_auth
from app.models import User, UserData, UserConfig

mail_pattern = '\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,}'

def verifiy_code(email: str, code: str):
    cache_code = VerificationCode(email)
    if cache_code.get() == code:
        cache_code.remove()
        return True

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

    configlist = ['vtype','pronounce', 'target', 'order']
    notin = [ v for v in configs.keys() if v in configlist ]
    if len(notin) != len(configlist):
        return {'message': 'Please provide correct config.'}, 400

    target = int(configs['target'])
    if not (target > 0 and target < 999):
        return {'message': 'Target must to be integer between 1 and 999'}, 400
    configs.update({'target': int(target)})
    
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

@api.route('/user/verification/<email>', methods=['GET'])
@limiter.limit('5 per hour') #限制每1小时请求5次
def get_confirm_code(email):
    if not email or not re.match(mail_pattern, email):
        return {'message': 'Please specify a valid email address.'}, 400

    code = generate_code()

    msg = Message(subject='[Light word] Verify your email address',
                  sender=current_app.config['MAIL_SENDER'],
                  recipients=[email])

    msg_body = '[Light word]: Your Authentication Code: %s \r\n<br>This code will expire in 1 hour\r\n<br>' % code
    
    msg_html = '''
    <p>[Light word]: Your Authentication Code: <b>%s<b></p>
    <p>This code will expire in 1 hour.</p>
    ''' % code

    send_email('[Light word] Verify your email address',
            sender=current_app.config['MAIL_SENDER'],
            recipients=[email],
            msg_body=msg_body,
            msg_html=msg_body)
    VerificationCode(email).set(code)
    
    return {'message': 'Ok'}

@api.route('/user/verification', methods=['POST'])
@limiter.limit('10 per hour') #限制每1小时请求10次
def mail_confirm_code():
    data = request.get_json()
    if not data:
        return {'message': 'You must provide JSON data.'}, 400

    user_mail = data.get('usermail', '').strip()
    user_code = data.get('code', '').strip()

    errors = []
    if not 'code' in data or not user_code:
        errors.append('Please provide a valid code.')
    if not 'usermail' in data or not re.match(mail_pattern, user_mail):
        errors.append('Please specify a valid email address.')

    if errors:
        return {'message': errors}, 400

    if verifiy_code(user_mail, user_code):
        return {'message': 'Ok'}
    
    return {'message': 'Verification code does not exist or is wrong'}, 400

@api.route('/user', methods=['POST'])
@limiter.limit('10 per hour') #限制每1小时请求10次
def create_user():
    data = request.get_json()
    if not data:
        return {'message': 'You must provide JSON data.'}, 400

    user_name = data.get('username', '').strip()
    user_mail = data.get('usermail', '').strip()
    user_pass = data.get('password', '').strip()
    user_code = data.get('code', '').strip()

    errors = []
    if not 'code' in data or not user_code:
        errors.append('Please provide a valid code.')
    if not 'username' in data or not user_name:
        errors.append('Please provide a valid username.')
    if not 'usermail' in data or not re.match(mail_pattern, user_mail):
        errors.append('Please specify a valid email address.')
    if not 'password' in data or not user_pass:
        errors.append('Please provide a valid password.')

    if errors:
        return {'message': errors}, 400

    if  User.query.filter_by(
        username = user_name
        ).first() or User.query.filter_by(
        usermail = user_mail
        ).first():
        return {'message': 'Username or Email address already exists'}, 400

    if verifiy_code(user_mail, user_code):
        user = User()
        user.username = user_name
        user.usermail = user_mail

        user.hash_password(user_pass)
        db.session.add(user)
        db.session.flush()
        UserConfig.init_config(user.uid)
        return jsonify({'token': user.generate_jwt(7200),
                        'token_type': 'Bearer', 
                        'expires_in': 7200}), 201
    
    return {'message': 'Verification code does not exist or is wrong'}, 400

@api.route('/user/reset', methods=['POST'])
@limiter.limit('10 per hour') #限制每1小时请求10次
def reset_user_pass():
    data = request.get_json()
    if not data:
        return {'message': 'You must provide JSON data.'}, 400

    user_mail = data.get('usermail', '').strip()
    user_pass = data.get('password', '').strip()
    user_code = data.get('code', '').strip()

    errors = []
    if not 'code' in data or not user_code:
        errors.append('Please provide a valid code.')
    if not 'usermail' in data or not re.match(mail_pattern, user_mail):
        errors.append('Please specify a valid email address.')
    if not 'password' in data or not user_pass:
        errors.append('Please provide a valid password.')

    if errors:
        return {'message': errors}, 400

    if verifiy_code(user_mail, user_code):
        user = User.query.filter_by(usermail = user_mail).first()
        user.usermail = user_mail
        user.hash_password(user_pass)
        db.session.commit()
        return jsonify({'message': 'Password reset successful.'}), 200
    
    return {'message': 'Verification code does not exist or is wrong.'}, 400