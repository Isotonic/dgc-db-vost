from ..api import api
from sqlalchemy import func
from .utils.resource import Resource
from .utils.namespace import Namespace
from ..utils.create import create_user
from ..utils.delete import delete_user
from ..models import User, Group, EmailLink
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.change import change_user_group, complete_registration, change_user_status
from .utils.models import id_model, create_user_modal, full_user_model, user_model, group_model, email_model, registration_model, task_model_with_incident, user_status_model

ns_user = Namespace('User', description='Used to carry out actions related to users.', path='/users')

@ns_user.route('')
class UsersEndpoint(Resource):
    @jwt_required
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


    @jwt_required
    @ns_user.expect(create_user_modal, validate=True)
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', user_model)
    @ns_user.response(400, 'Name is empty')
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(403, 'Missing supervisor permission')
    @ns_user.response(409, 'Account already exists with email')
    @api.marshal_with(user_model)
    def post(self):
        """
                Creates a new user, requires the supervisor permission. Supplying a group is optional and can be omitted.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        ns_user.has_permission(current_user, 'supervisor')
        user = User.query.filter(func.lower(User.email) == func.lower(payload['email'])).first()
        if user is not None:
            ns_user.abort(409, 'Account already exists with email')

        group = None
        if 'group' in api.payload.keys():
            group = Group.query.filter_by(id=payload['group']).first()
            if not group:
                ns_user.abort(401, 'Group doesn\'t exist')

        created_user = create_user(payload['email'], group, current_user)
        if created_user is False:
            ns_user.abort(400, 'Name is empty')
        return created_user, 200


@ns_user.route('/me')
class CurrentUserEndpoint(Resource):
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
class UserEndpoint(Resource):
    @jwt_required
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


    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success')
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(403, 'Missing incident access')
    @ns_user.response(403, 'Missing supervisor permission')
    @ns_user.response(404, 'User doesn\'t exist')
    def delete(self, user):
        """
                Revokes registation email sent to user, requires the supervisor permission.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_user.has_permission(current_user, 'supervisor')
        delete_user(user, current_user)
        return 'Success', 200


@ns_user.route('/<int:id>/resend-email')
@ns_user.doc(params={'id': 'User ID.'})
@ns_user.resolve_object('user', lambda kwargs: User.query.get_or_error(kwargs.pop('id')))
class UserGroupEndpoint(Resource):
    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success')
    @ns_user.response(401, 'User has no email to resend')
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(404, 'User doesn\'t exist')
    def post(self, user):
        """
                Resends the registration email to the user, requires the supervisor permission.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_user.has_permission(current_user, 'supervisor')
        email = EmailLink.query.filter_by(user_id=user.id, verify=True).first()
        if not email:
            ns_user.abort(404, 'User has no email to resend')
        email.send_registration_email()
        return 'Success', 200


@ns_user.route('/verify-registration-link/<string:link>')
@ns_user.doc(params={'link': 'End path of the link.'})
class RegistrationLinkEndpoint(Resource):
    @ns_user.response(200, 'Success', email_model)
    @ns_user.response(404, 'Registration link doesn\'t exist')
    @api.marshal_with(email_model)
    def get(self, link):
        """
                Returns if a registration link is valid or not.
        """
        email = EmailLink.query.filter_by(link=link, verify=True).first()
        if not email:
            ns_user.abort(404, 'Registration link doesn\'t exist')
        return email.user, 200


@ns_user.route('/complete-registration/<string:link>')
@ns_user.doc(params={'path': 'End path of the link.'})
class RegistrationEndpoint(Resource):
    @ns_user.expect(registration_model, validate=True)
    @ns_user.response(200, 'Success')
    @ns_user.response(400, 'Firstname is empty')
    @ns_user.response(400, 'Surname is empty')
    @ns_user.response(400, 'Password is empty')
    @ns_user.response(400, 'Password does not meet the requirements')
    @ns_user.response(404, 'Registration link doesn\'t exist')
    def put(self, link):
        """
                Complete's a user's registration.
        """
        email = EmailLink.query.filter_by(link=link, verify=True).first()
        if not email:
            ns_user.abort(404, 'Registration link doesn\'t exist')

        payload = api.payload
        if payload['firstname'] == '':
            ns_user.abort(400, 'Firstname is empty')
        elif payload['surname'] == '':
            ns_user.abort(400, 'Firstname is empty')
        elif payload['password'] == '':
            ns_user.abort(400, 'Firstname is empty')

        if complete_registration(email, payload['firstname'], payload['surname'], payload['password']) is False:
            ns_user.abort(400, 'Password does not meet the requirements')
        return 'Success', 200


@ns_user.route('/<int:id>/status')
@ns_user.doc(params={'id': 'User ID.'})
@ns_user.resolve_object('user', lambda kwargs: User.query.get_or_error(kwargs.pop('id')))
class UserStatusEndpoint(Resource):
    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', user_status_model)
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(404, 'User doesn\'t exist')
    @api.marshal_with(user_status_model)
    def get(self, user):
        """
                Returns user's' info.
        """
        return user.status, 200


    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.expect(id_model, validate=True)
    @ns_user.response(200, 'Success', user_status_model)
    @ns_user.response(400, 'User already had this status')
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(403, 'Missing supervisor permission')
    @ns_user.response(403, 'Can\'t change your own status')
    @ns_user.response(404, 'User doesn\'t exist')
    @api.marshal_with(user_status_model)
    def put(self, user):
        """
                Changes a user's status, requires the supervisor permission.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        ns_user.has_permission(current_user, 'supervisor')
        if current_user == user:
            ns_user.abort(403, 'Can\'t change your own status')

        if change_user_status(user, payload['status'], current_user) is False:
            ns_user.abort(400, 'User already has this status')
        return user.status, 200


@ns_user.route('/<int:id>/group')
@ns_user.doc(params={'id': 'User ID.'})
@ns_user.resolve_object('user', lambda kwargs: User.query.get_or_error(kwargs.pop('id')))
class UserGroupEndpoint(Resource):
    @jwt_required
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


    @jwt_required
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
                Changes a user's group, requires the supervisor permission. Supply a group ID, can be omitted.
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


@ns_user.route('/me/tasks')
class UserTasksEndpoint(Resource):
    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [task_model_with_incident])
    @ns_user.response(401, 'Incorrect credentials')
    @api.marshal_with(task_model_with_incident)
    def get(self):
        """
                Returns user's assigned tasks.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        return current_user.tasks, 200
