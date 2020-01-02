from flask import url_for
from sqlalchemy import func
from app.api import dgvost_api
from app.models import User, Group
from app.utils.create import create_user
from flask_restplus import Resource, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.utils.models import new_user_model, user_model, incident_model

ns_user = Namespace('User', description='Used to carry out operations related to users.', path='/user')


@ns_user.route('/list')
class GetAllUsers(Resource):
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


@ns_user.route('/get/<int:user_id>')
class GetUser(Resource):
    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [user_model])
    @ns_user.response(401, 'User doesn\'t exist')
    def get(self, user_id):
        """
                Returns user info.
        """
        user = User.query.filter_by(id=user_id).first()
        if not user:
            ns_user.abort(401, 'User doesn\'t exist')
        return {'id': user.id, 'firstname': user.firstname, 'surname': user.surname, 'avatar_url': url_for('static', filename=user.get_avatar(static=False), _external=True), 'group_id': user.group_id}, 200


@ns_user.route('/create')
class CreateNewUser(Resource):
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
        payload = dgvost_api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        if not current_user.group.has_permission('Supervisor'):
            ns_user.abort(403, 'Missing Supervisor permission')
        user = User.query.filter(func.lower(User.email) == func.lower(payload['email'])).first()
        if user is not None:
            ns_user.abort(409, 'Username or email already exists')

        group = None
        if 'group_id' in dgvost_api.payload.keys():
            group = Group.query.filter_by(id=payload['group_id']).first()
            if not group:
                ns_user.abort(401, 'Group doesn\'t exist')

        created_user = create_user(payload['firstname'], payload['surname'], payload['email'], group.id, current_user)
        return {'user_id': created_user.id, 'firstname': created_user.firstname, 'surname': created_user.surname, 'avatar_url': url_for('static', filename=created_user.get_avatar(static=False), _external=True), 'group_id': created_user.group_id}, 200

@ns_user.route('/openincidents')
class GetAllOpenIncidents(Resource):
    @jwt_required
    @ns_user.doc(security='access_token')
    @ns_user.response(200, 'Success', [incident_model])
    def get(self):
        """
                Returns all open incidents the user has access to.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        deployments = current_user.get_deployments()
        incidents = [y for x in [current_user.get_incidents(m) for m in deployments] for y in x]
        all_incidents = [{'id': m.id, 'name': m.name, 'description': m.description,
                          'location': m.location, 'open': m.open_status, 'public': m.public,
                          'flagged': m.flagged, 'type': m.incident_type, 'priority': m.priority,
                          'longitude': m.longitude, 'latitude': m.latitude,
                          'created_at': m.created_at.timestamp()} for m in incidents]
        return all_incidents, 200