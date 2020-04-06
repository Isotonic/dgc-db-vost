from ..api import api
from os import SEEK_END
from sqlalchemy import func
from flask_socketio import emit
from flask_restx import reqparse
from .utils.resource import Resource
from .utils.namespace import Namespace
from ..utils.delete import delete_user
from ..models import User, Group, EmailLink
from werkzeug.datastructures import FileStorage
from ..utils.create import create_user, create_password_reset_email
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from ..utils.change import change_user_group, edit_user_details, complete_registration, change_user_password, change_user_status
from .utils.models import id_model, create_user_modal, user_model, user_admin_panel_model, user_full_details_model, group_model, email_model, registration_model, password_reset_model, task_model_with_incident, user_status_model, edit_user_details_model, updated_user_details_model, avatar_model

ns_user = Namespace('User', description='Used to carry out actions related to users.', path='/users')

upload_parser = reqparse.RequestParser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)


def validateFileSize(file):
    file.seek(0, SEEK_END)
    size = file.tell()
    if size > 10485760:
        return False
    file.seek(0)
    return True


def validateExtension(filename):
    return '.' in filename and filename.split('.')[-1] in ['jpg', 'jpeg', 'png']


@ns_user.route('')
class UsersEndpoint(Resource):
    @jwt_required
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


@ns_user.route('/detailed')
class UsersEndpoint(Resource):
    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [user_admin_panel_model])
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(403, 'Missing supervisor permission')
    @api.marshal_with(user_admin_panel_model)
    def get(self):
        """
                Returns all users with more details.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        ns_user.has_permission(current_user, 'supervisor')
        return User.query.all(), 200


@ns_user.route('/me')
class CurrentUserEndpoint(Resource):
    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', user_full_details_model)
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(403, 'Account was disabled')
    @api.marshal_with(user_full_details_model)
    def get(self):
        """
                Returns user info of the current user.
        """
        user = User.query.filter_by(id=get_jwt_identity()).first()
        return user, 200


    @jwt_required
    @ns_user.expect(edit_user_details_model, validate=True)
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', updated_user_details_model)
    @ns_user.response(400, 'Firstname is empty')
    @ns_user.response(400, 'Surname is empty')
    @ns_user.response(400, 'Email is empty')
    @ns_user.response(400, 'New Password is empty')
    @ns_user.response(400, 'New password does not meet the requirements')
    @ns_user.response(400, 'You already have these details set')
    @ns_user.response(400, 'Password is incorrect')
    @ns_user.response(401, 'Incorrect credentials')
    def put(self):
        """
                Edits user's account settings.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        if payload['firstname'] == '':
            ns_user.abort(400, 'Firstname is empty')
        elif payload['surname'] == '':
            ns_user.abort(400, 'Surname is empty')
        elif payload['email'] == '':
            ns_user.abort(400, 'Email is empty')
        elif payload['currentPassword'] == '':
            ns_user.abort(400, 'Password is empty')
        elif 'newPassword' in payload.keys() and payload['newPassword'] == '':
            ns_user.abort(400, 'Password is empty')

        new_password = None
        if 'newPassword' in payload.keys():
            new_password = payload['newPassword']
        elif current_user.firstname == payload['firstname'] and current_user.surname == payload['surname'] and current_user.email == payload['email']:
            ns_user.abort(401, 'You already have these details set')

        if not current_user.check_password(api.payload['currentPassword']):
            ns_user.abort(401, 'Password is incorrect')

        if edit_user_details(current_user, payload['firstname'], payload['surname'], payload['email'], new_password) is False:
            ns_user.abort(400, 'Password does not meet the requirements')

        if new_password:
            access_token = create_access_token(identity=current_user.id)
            refresh_token = create_refresh_token(identity=current_user.id)

            return {'firstname': current_user.firstname, 'surname': current_user.surname, 'email': current_user.email, 'access_token': access_token, 'refresh_token': refresh_token}, 200
        else:
            return {'firstname': current_user.firstname, 'surname': current_user.surname, 'email': current_user.email}, 200


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
            ns_user.abort(400, 'Surname is empty')
        elif payload['password'] == '':
            ns_user.abort(400, 'Password is empty')

        if complete_registration(email, payload['firstname'], payload['surname'], payload['password']) is False:
            ns_user.abort(400, 'Password does not meet the requirements')
        return 'Success', 200


@ns_user.route('/request-password-reset')
class RegistrationEndpoint(Resource):
    @ns_user.expect(email_model, validate=True)
    @ns_user.response(200, 'Success')
    @ns_user.response(400, 'Firstname is empty')
    @ns_user.response(400, 'Surname is empty')
    @ns_user.response(400, 'Password is empty')
    @ns_user.response(400, 'Password does not meet the requirements')
    @ns_user.response(404, 'User with email doesn\'t exist')
    def post(self):
        """
                Sends a password reset email to the user.
        """
        user = User.query.filter(func.lower(User.email) == func.lower(api.payload['email'])).first()
        if not user or user.status < 1:
            ns_user.abort(404, 'User with email doesn\'t exist')

        create_password_reset_email(user)
        return 'Success', 200


@ns_user.route('/verify-password-reset-link/<string:link>')
@ns_user.doc(params={'link': 'End path of the link.'})
class PasswordLinkEndpoint(Resource):
    @ns_user.response(200, 'Success', email_model)
    @ns_user.response(404, 'Password reset link doesn\'t exist')
    @api.marshal_with(email_model)
    def get(self, link):
        """
                Returns if a password reset link is valid or not.
        """
        email = EmailLink.query.filter_by(link=link, forgot_password=True).first()
        if not email or email.user.status < 1:
            ns_user.abort(404, 'Password reset link doesn\'t exist')
        return email.user, 200


@ns_user.route('/password-reset/<string:link>')
@ns_user.doc(params={'path': 'End path of the link.'})
class PasswordResetEndpoint(Resource):
    @ns_user.expect(password_reset_model, validate=True)
    @ns_user.response(200, 'Success')
    @ns_user.response(400, 'Password is empty')
    @ns_user.response(400, 'Password does not meet the requirements')
    @ns_user.response(404, 'Password reset link doesn\'t exist')
    def put(self, link):
        """
                Reset the user's password.
        """
        email = EmailLink.query.filter_by(link=link, forgot_password=True).first()
        if not email or email.user.status < 1:
            ns_user.abort(404, 'Password reset link doesn\'t exist')

        payload = api.payload
        if payload['password'] == '':
            ns_user.abort(400, 'Password is empty')

        if change_user_password(email, payload['password']) is False:
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
    @ns_user.expect(user_status_model, validate=True)
    @ns_user.response(200, 'Success', user_status_model)
    @ns_user.response(400, 'User already had this status')
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(401, 'Invalid status')
    @ns_user.response(403, 'Missing supervisor permission')
    @ns_user.response(403, 'Can\'t change your own status')
    @ns_user.response(403, 'Can\'t change a superuser\'s status')
    @ns_user.response(404, 'User doesn\'t exist')
    @api.marshal_with(user_status_model)
    def put(self, user):
        """
                Changes a user's status, requires the supervisor permission.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        ns_user.has_permission(current_user, 'supervisor')
        if payload['status'] not in [1, -1]:
            ns_user.abort(401, 'Invalid status')

        if current_user == user:
            ns_user.abort(403, 'Can\'t change your own status')

        if user.status == 2:
            ns_user.abort(403, 'Can\'t change a superuser\'s status')

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
    @ns_user.response(403, 'Can\'t change your own group')
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
        if current_user == user:
            ns_user.abort(403, 'Can\'t change your own group')
        if 'id' in payload.keys():
            group = Group.query.filter_by(id=payload['id']).first()
            if not group:
                ns_user.abort(404, 'Group doesn\'t exist')
        else:
            group = None

        if change_user_group(user, group, current_user) is False:
            ns_user.abort(400, 'User already has this group')
        return user.group, 200


@ns_user.route('/avatar')
class UserTasksEndpoint(Resource):
    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [avatar_model])
    @ns_user.response(401, 'Incorrect credentials')
    @api.marshal_with(avatar_model)
    def get(self):
        """
                Returns user's avatar.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        return current_user, 200


    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [avatar_model])
    @ns_user.response(401, 'Incorrect credentials')
    @ns_user.response(401, 'No file attached')
    @ns_user.response(401, 'Invalid file type')
    @ns_user.response(401, 'Image too big, must be less than 10MB')
    @api.marshal_with(avatar_model)
    def post(self):
        """
                Changes user's avatar, must be a PNG, JPEG or JPEG and less than 10MB.
        """
        data = upload_parser.parse_args()
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        if not 'file' in data.keys() or not data['file']:
            ns_user.abort(401, 'No file attached')

        image = data['file']

        if not validateExtension(image.filename):
            ns_user.abort(401, 'Invalid file type')
        if not validateFileSize(image):
            ns_user.abort(401, 'Image too big, must be less than 10MB')

        current_user.save_avatar(image)
        emit('CHANGE_USER_AVATAR', {'avatarUrl': current_user.get_avatar(), 'code': 200}, namespace='/', room=f'{current_user.id}')
        emit('CHANGE_USERS_AVATAR', {'id': current_user.id, 'avatarUrl': current_user.get_avatar(), 'code': 200}, namespace='/', room='all')
        return current_user, 200


    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [avatar_model])
    @ns_user.response(401, 'Incorrect credentials')
    @api.marshal_with(avatar_model)
    def delete(self):
        """
                Deletes user's avatar.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        current_user.delete_avatar()
        emit('CHANGE_USER_AVATAR', {'avatarUrl': current_user.get_avatar(), 'code': 200}, namespace='/', room=f'{current_user.id}')
        emit('CHANGE_USERS_AVATAR', {'id': current_user.id, 'avatarUrl': current_user.get_avatar(), 'code': 200}, namespace='/', room='all')
        return current_user, 200


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
