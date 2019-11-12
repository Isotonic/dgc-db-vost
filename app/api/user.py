from flask import url_for
from app.api import c5_api
from sqlalchemy import func
from app.models import User, Group
from app.utils.create import new_user
from flask_restplus import Resource, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.utils.models import new_user_model, user_model

ns_user = Namespace('User', description='Used to carry out operations related with users.', path='/user')


@ns_user.route('/list')
class get_all_users(Resource):
    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [user_model])
    @ns_user.response(404, 'No users exist')
    def get(self):
        """
                Returns all users.
        """
        all_users = [{'id': m.id, 'firstname': m.firstname, 'surname': m.surname, 'avatar_url': url_for('static', filename=m.get_avatar(static=False), _external=True), 'group_id': m.group_id} for m in User.query.all()]
        if not all_users:
            ns_user.abort(404, 'No users exist')
        return all_users, 200


@ns_user.route('/get/<int:id>')
class get_user(Resource):
    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [user_model])
    @ns_user.response(401, "User doesn't exist")
    def get(self, id):
        """
                Returns user info.
        """
        user = User.query.filter_by(id=id).first()
        if not user:
            ns_user.abort(401, "User doesn't exist")
        return {'id': user.id, 'firstname': user.firstname, 'surname': user.surname, 'avatar_url': url_for('static', filename=user.get_avatar(static=False), _external=True), 'group_id': user.group_id}, 200


@ns_user.route('/create')
class create_new_user(Resource):
    @jwt_required
    @ns_user.expect(new_user_model, validate=True)
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', user_model)
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(403, 'Missing Supervisor permission')
    def post(self):
        """
                Creates a new user, requires the Supervisor permission. Supplying a group is optional.
        """
        payload = c5_api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        if not current_user.group.has_permission('Supervisor'):
            ns_user.abort(403, 'Missing Supervisor permission')
        user = User.query.filter(func.lower(User.email) == func.lower(payload['email'])).first()
        if user is not None:
            ns_user.abort(409, 'Username or email already exists')

        group = None
        if 'group_id' in c5_api.payload.keys():
            group = Group.query.filter_by(id=payload['group_id']).first()
            if not group:
                ns_user.abort(401, "Group doesn't exist")

        created_user = new_user(payload['firstname'], payload['surname'], payload['email'], group.id, current_user)
        return {'user_id': created_user.id, 'firstname': created_user.firstname, 'surname': created_user.surname, 'avatar_url': url_for('static', filename=created_user.get_avatar(static=False), _external=True), 'group_id': created_user.group_id}, 200
