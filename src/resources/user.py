from flask_restful import Resource, reqparse
from models import db, User

parser = reqparse.RequestParser()
parser.add_argument('email', required=True)
parser.add_argument('passwordHash', required=True)
parser.add_argument('role', required=True)
parser.add_argument('isActive', type=bool, required=True)

class UserListResource(Resource):
    def get(self):
        users = User.query.all()
        return [{'id': u.id, 'email': u.email, 'role': u.role, 'isActive': u.isActive} for u in users]

    def post(self):
        args = parser.parse_args()
        user = User(**args)
        db.session.add(user)
        db.session.commit()
        return {'message': 'User created', 'id': user.id}, 201

class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return {'id': user.id, 'email': user.email, 'role': user.role, 'isActive': user.isActive}

    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        args = parser.parse_args()
        for key, value in args.items():
            setattr(user, key, value)
        db.session.commit()
        return {'message': 'User updated'}

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted'}
