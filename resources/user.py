from werkzeug.security import safe_str_cmp
from flask import jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, jwt_required, get_raw_jwt, get_jwt_claims, decode_token
from flask_restful import Resource, reqparse
from models.user import UserModel
from blacklist import BLACKLIST

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username', type=str, required=True, help="'username' field cannot be left blank.")
_user_parser.add_argument('password', type=str, required=True, help="'password' field cannot be left blank.")

class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()
        if UserModel.find_by_username(data['username']):
            return {"message": "User with that username already exists."}, 201
        else:
            user = UserModel(**data)
            user.save_to_db()
            return {"message": "User created successfully."}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found.'}, 404
        return user.json()

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User not found.'}, 404
        user.delete_from_db()
        return {'message': "User deleted."}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()
        user = UserModel.find_by_username(data['username'])
        if user and safe_str_cmp(user.password, data['password']):
            refresh_token = create_refresh_token(user.id)
            admin = (user.id == 1)
            access_token = create_access_token(identity=user.id, fresh=True, user_claims={'refresh_token': refresh_token, 'is_admin': admin})
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200
        return {'message': 'Invalid credentials.'}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        refresh = get_jwt_claims()['refresh_token']
        refresh_jti = decode_token(refresh)['jti']
        jti = get_raw_jwt()['jti']
        BLACKLIST.add(refresh_jti)
        BLACKLIST.add(jti)
        return jsonify({"blacklist": list(BLACKLIST)})


class UserList(Resource):
    def get(self):
        return {'users': [user.json() for user in UserModel.query.all()]}


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}
