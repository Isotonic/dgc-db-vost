from app.api import api
from sqlalchemy import func
from app.models import User, Group
from app.utils.create import create_user
from app.api.utils.resource import Resource
from app.api.utils.namespace import Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.utils.models import create_user_modal, user_model, incident_model

ns_user = Namespace('User', description='Used to carry out operations related to users.', path='/users')

@ns_user.route('')
class AllUsers(Resource):
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [user_model])
    @ns_user.response(401, 'Incorrect credentials')
    @api.marshal_with(user_model)
    def get(self):
        """
                Returns all users.
        """
        return User.query.all(), 200


    @jwt_required
    @ns_user.expect(create_user_modal, validate=True)
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', user_model)
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(403, 'Missing Supervisor permission')
    @api.marshal_with(user_model)
    def post(self):
        """
                Creates a new user, requires the Supervisor permission. Supplying a group is optional.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        ns_user.has_permission(current_user, 'supervisor')
        user = User.query.filter(func.lower(User.email) == func.lower(payload['email'])).first()
        if user is not None:
            ns_user.abort(409, 'Username or email already exists')

        group = None
        if 'group_id' in api.payload.keys():
            group = Group.query.filter_by(id=payload['group_id']).first()
            if not group:
                ns_user.abort(401, 'Group doesn\'t exist')

        created_user = create_user(payload['firstname'], payload['surname'], payload['email'], group.id, current_user)
        return created_user, 200


@ns_user.route('/me')
class GetCurrentUser(Resource):
    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', user_model)
    @api.marshal_with(user_model)
    def get(self):
        """
                Returns user info of the current user.
        """
        user = User.query.filter_by(id=get_jwt_identity()).first()
        return user, 200


@ns_user.route('/<int:id>')
@ns_user.doc(params={'id': 'User ID.'})
@ns_user.resolve_object('user', lambda kwargs: User.query.get_or_error(kwargs.pop('id')))
class GetUser(Resource):
    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [user_model])
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(404, 'User doesn\'t exist')
    @api.marshal_with(user_model)
    def get(self, user):
        """
                Returns user info.
        """
        return user, 200
