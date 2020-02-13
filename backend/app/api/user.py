from ..api import api
from sqlalchemy import func
from ..models import User, Group
from .utils.resource import Resource
from .utils.namespace import Namespace
from ..utils.create import create_user
from ..utils.change import change_user_group
from flask_jwt_extended import jwt_required, get_jwt_identity
from .utils.models import id_model, create_user_modal, full_user_model, user_model, group_model

ns_user = Namespace('User', description='Used to carry out actions related to users.', path='/users', decorators=[jwt_required])

@ns_user.route('')
class UsersEndpoint(Resource):
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [full_user_model])
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(403, 'Missing supervisor permission')
    @api.marshal_with(full_user_model)
    def get(self):
        """
                Returns all users.
        """
        return User.query.all(), 200


    @ns_user.expect(create_user_modal, validate=True)
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', user_model)
    @ns_user.response(400, 'Name is empty')
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(403, 'Missing supervisor permission')
    @api.marshal_with(user_model)
    def post(self):
        """
                Creates a new user, requires the supervisor permission. Supplying a group is optional.
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
        if created_user is False:
            ns_user.abort(400, 'Name is empty')
        return created_user, 200


@ns_user.route('/me')
class CurrentUserEndpoint(Resource):
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
class UserEndpoint(Resource):
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', user_model)
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(404, 'User doesn\'t exist')
    @api.marshal_with(user_model)
    def get(self, user):
        """
                Returns user info.
        """
        return user, 200


@ns_user.route('/<int:id>/group')
@ns_user.doc(params={'id': 'User ID.'})
@ns_user.resolve_object('user', lambda kwargs: User.query.get_or_error(kwargs.pop('id')))
class UserGroupEndpoint(Resource):
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', group_model)
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(404, 'User doesn\'t exist')
    @api.marshal_with(group_model)
    def get(self, user):
        """
                Returns user group info.
        """
        return user.group, 200


    @ns_user.doc(security='access_token')
    @ns_user.expect(id_model, validate=True)
    @ns_user.response(200, 'Success', group_model)
    @ns_user.response(400, 'User already has this group')
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(403, 'Missing supervisor permission')
    @ns_user.response(404, 'User doesn\'t exist')
    @ns_user.response(404, 'Group doesn\'t exist')
    @api.marshal_with(group_model)
    def put(self, user):
        """
                Changes a user's, requires the supervisor permission. Supply a group ID, can be null.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        ns_user.has_permission(current_user, 'supervisor')
        if 'id' in payload.keys():
            group = Group.query.filter_by(id=payload['id']).first()
            if not group:
                ns_user.abort(404, 'Group doesn\'t exist')
        else:
            group = None


        if change_user_group(user, group, current_user) is False:
            ns_user.abort(400, 'User already has this group')
        return user.group, 200
