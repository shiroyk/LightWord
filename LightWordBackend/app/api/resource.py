import os
from flask import jsonify, g, request, abort, current_app
from werkzeug.utils import secure_filename

from app import db
from app.api import api
from app.api.auth import token_auth
from app.utils import ExerciseBuild, get_gspeech, VocabTypeCache, ConfigCache, DailyStatisticCache
from app.models import VocabType, UserData

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']

vocabtype_cache = VocabTypeCache()

@api.route('/resource/exercise', methods=['GET'])
@token_auth.login_required
def get_exercise():
    n = request.args.get('n', default = 10, type = int)
    config = ConfigCache().get()
    Exercise = ExerciseBuild(g.user.uid, **config)
    return jsonify(list(Exercise.auto_exercise(n)))

@api.route('/resource/exercise/speech', methods=['POST'])
@token_auth.login_required
def get_speech():
    data = request.get_json()
    if not data:
        return {'message': 'You must provide JSON data.'}, 400
    return get_gspeech(data['text'])

@api.route('/resource/exercise/status', methods=['PUT'])
@token_auth.login_required
def practice():
    data = request.get_json()
    if not data:
        return {'message': 'You must provide JSON data.'}, 400

    errors = {}
    if not 'word' in data or not data.get('word', None):
        errors['word'] = 'Error word id.'
    if not 'vtype' in data or not data.get('vtype', None):
        errors['vtype'] = 'Error vocab type id.'
    if not 'status' in data or not data.get('status', None):
        errors['status'] = 'Error status.'

    if errors:
        return jsonify({'message': errors}), 400
    
    userdata = {
        'uid': g.user.uid,
        'wid': data['word'],
        'tid': data['vtype']
    }
    statistic = DailyStatisticCache()
    if data['status'] == 1:
        if UserData.remember(**userdata):
            statistic.increase(1)
    elif data['status'] == 2:
        if UserData.forget(**userdata):
            statistic.increase(2)
    elif data['status'] == 3:
        if UserData.remembered(**userdata):
            statistic.increase(1)
    else:
        return {'message': 'Error status.'}, 400
    
    return jsonify(statistic.get())
    
@api.route('/resource/type', methods=['GET'])
@token_auth.login_required
def get_vtype():
    return jsonify(vocabtype_cache.get())

@api.route('/resource/type', methods=['POST'])
@token_auth.login_required
def upload_txt():
    if g.user.username != current_app.config['FLASKY_ADMIN']:
        return {'message': 'Only admin can unpload file!!!'}, 403
    file = request.files['file']
    filename = secure_filename(file.filename)
    if file and allowed_file(filename):
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    else:
        return {'message': 'Please check the file type!!!'}, 415
    return {'message': 'Ok'}, 201

@api.route('/resource/type', methods=['PUT'])
@token_auth.login_required
def put_vtype():
    data = request.get_json()
 
    if not data:
        return {'message': 'You must provide JSON data.'}, 400

    errors = []
    if not 'id' in data or not data.get('id', None):
        errors.append('Error vocab name id.')
    if not 'alias' in data or not data.get('alias', None).strip():
        errors.append('Error alias name.')

    if errors:
        return {'message': errors}, 400
    vocabtype_cache.remove()
    vtype = VocabType.query.get(data['id'])
    if not vtype:
        return {'message': 'Error vocab name id.'}, 400
    vtype.alias = data['alias']
    db.session.commit()
    return jsonify(vocabtype_cache.get())

