from flask import jsonify, request
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt_identity, jwt_required,
                                set_refresh_cookies)

from app import db
from app.api import bp
from app.api.auth import basic_auth, token_auth
from app.models import User


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()
    return jsonify({'token': token})

@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    token_auth.current_user().revoke_token()
    db.session.commit()
    return '', 204

@bp.route('/login', methods=['POST'])
def jwt_login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)
        response = jsonify({
            'access_token': access_token,
        })
        set_refresh_cookies(response, refresh_token)
        return response
    return {"message": "Invalid Credentials"}, 401


@bp.route('/refresh-token', methods=['POST'])
@jwt_required(refresh=True, locations=["cookies"])
def refresh_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)
