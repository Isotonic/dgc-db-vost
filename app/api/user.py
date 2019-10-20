from app.api import c5_api
from app.models import User, Group
from app.utils.create import new_user
from flask_restplus import Resource, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.utils.models import new_user_model, return_user, all_users_model

ns_user = Namespace('User', description='Used to carry out operations to do with users.', path='/user')


@ns_user.route('/list')
class get_all_users(Resource):
    # @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [all_users_model])
    @ns_user.response(404, 'No groups exist')
    def post(self):
        """
                Returns all groups.
        """
        all_users = [{"name": m.name, "permissions": m.permissions} for m in Group.query.all()]
        if not all_users:
            ns_user.abort(404, 'No groups exist')
        return all_users, 200


@ns_user.route('/create')
class create_new_user(Resource):
    @jwt_required
    @ns_user.expect(new_user_model, validate=True)
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', return_user)
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(403, 'Missing Supervisor permission')
    def post(self):
        """
                Creates a new user, requires the Supervisor permission. Supplying a group is optional.
        """
        payload = c5_api.payload
        current_user = User.query.filter_by(username=get_jwt_identity()).first()

        if not current_user.group.has_permission('Supervisor'):
            ns_user.abort(403, 'Missing Supervisor permission')

        user = User.query.filter((User.username == payload['username']) | (User.email == payload['email'])).first()
        if user is not None:
            ns_user.abort(409, 'Username or email already exists')

        group = None
        if "group" in c5_api.payload.keys():
            group = Group.query.filter_by(name=payload['group']).first()
            if not group:
                ns_user.abort(401, "Group doesn't exist")

        created_user = new_user(payload['username'], payload['email'], group.id, current_user)
        return {"user_id": created_user.id, "username": created_user.username, "group": created_user.group.name}, 200
