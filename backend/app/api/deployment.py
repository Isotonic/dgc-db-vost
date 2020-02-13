from ..api import api
from .utils.resource import Resource
from .utils.namespace import Namespace
from ..utils.change import edit_deployment
from ..models import User, Group, Deployment
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.create import create_deployment, create_incident
from .utils.models import new_deployment_model, deployment_model, new_incident_model, incident_model, user_model, group_model

ns_deployment = Namespace('Deployment', description='Used to carry out actions related to deployments.', path='/deployments', decorators=[jwt_required])


@ns_deployment.route('')
class DeploymentsEndpoint(Resource):
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', [deployment_model])
    @ns_deployment.response(401, 'Incorrect credentials')
    @api.marshal_with(deployment_model)
    def get(self):
        """
                Returns all deployments the user has access to.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        all_deployments = current_user.get_deployments()
        return all_deployments, 200


    @ns_deployment.expect(new_deployment_model, validate=True)
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', deployment_model)
    @ns_deployment.response(400, 'Name or description is empty')
    @ns_deployment.response(401, 'Incorrect credentials')
    @ns_deployment.response(403, 'Missing supervisor permission')
    @api.marshal_with(deployment_model)
    def post(self):
        """
                Creates a new deployment, requires the supervisor permission. Supplying a list of groups and users is optional and if omitted then everyone has access.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_deployment.has_permission(current_user, 'supervisor')

        if 'users' in payload.keys():
            users = payload['users']
        else:
            users = []

        if 'groups' in payload.keys():
            groups = payload['groups']
        else:
            groups = []

        deployment = create_deployment(payload['name'], payload['description'], groups, users, current_user)
        if deployment is False:
            ns_deployment.abort(400, 'Name or description is empty')
        return deployment, 200


@ns_deployment.route('/<int:id>')
@ns_deployment.doc(params={'id': 'Deployment ID.'})
@ns_deployment.resolve_object('deployment', lambda kwargs: Deployment.query.get_or_error(kwargs.pop('id')))
class DeploymentEndpoint(Resource):
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', [deployment_model])
    @ns_deployment.response(401, 'Incorrect credentials')
    @ns_deployment.response(403, 'Missing deployment access')
    @ns_deployment.response(404, 'Deployment doen\'t exist')
    @api.marshal_with(deployment_model)
    def get(self, deployment):
        """
                Returns deployment info.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_deployment.has_deployment_access(current_user, deployment)
        return deployment, 200


    @ns_deployment.expect(new_incident_model, validate=True)
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', incident_model)
    @ns_deployment.response(400, 'Name is empty')
    @ns_deployment.response(401, 'Incorrect credentials')
    @ns_deployment.response(403, 'Missing deployment access')
    @ns_deployment.response(404, 'Deployment doesn\'t exist')
    @api.marshal_with(deployment_model)
    def post(self, deployment):
        """
                Creates a new incident.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        created_incident = create_incident(payload['name'], payload['description'], payload['location'], payload['reported_via'], payload['reference'], deployment, current_user)
        if created_incident is False:
            ns_deployment.abort(400, 'Name is empty')
        return created_incident, 200


    @ns_deployment.expect(new_deployment_model, validate=True)
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', deployment_model)
    @ns_deployment.response(400, 'Name is empty')
    @ns_deployment.response(400, 'Description is empty')
    @ns_deployment.response(400, 'Deployment already has these settings')
    @ns_deployment.response(401, 'Incorrect credentials')
    @ns_deployment.response(403, 'Missing supervisor permission')
    @api.marshal_with(deployment_model)
    def put(self, deployment):
        """
                Edits deployment, requires the supervisor permission. Supplying a list of groups and users is optional and if omitted then everyone has access.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_deployment.has_permission(current_user, 'supervisor')

        if payload['name'] == '':
            ns_deployment.abort(400, 'Name is empty')

        if payload['description'] == '':
            ns_deployment.abort(400, 'Description is empty')

        if 'users' in payload.keys():
            users = payload['users']
        else:
            users = []

        if 'groups' in payload.keys():
            groups = payload['groups']
        else:
            groups = []

        if edit_deployment(deployment, payload['name'], payload['description'], groups, users, current_user) is False:
            ns_deployment.abort(400, 'Deployment already has these settings')
        return deployment, 200


@ns_deployment.route('/<int:id>/incidents')
@ns_deployment.doc(params={'id': 'Deployment ID.'})
@ns_deployment.resolve_object('deployment', lambda kwargs: Deployment.query.get_or_error(kwargs.pop('id')))
class IncidentsEndpoint(Resource):
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', [incident_model])
    @ns_deployment.response(401, 'Incorrect credentials')
    @ns_deployment.response(403, 'Missing deployment access')
    @ns_deployment.response(404, 'Deployment doesn\'t exist')
    @api.marshal_with(incident_model)
    def get(self, deployment):
        """
                Returns all incidents the user has access to.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_deployment.has_deployment_access(current_user, deployment)
        all_incidents = current_user.get_incidents(deployment.id)
        return all_incidents, 200


@ns_deployment.route('/<int:id>/open-incidents')
@ns_deployment.doc(params={'id': 'Deployment ID.'})
@ns_deployment.resolve_object('deployment', lambda kwargs: Deployment.query.get_or_error(kwargs.pop('id')))
class OpenIncidentsEndpoint(Resource):
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', [incident_model])
    @ns_deployment.response(401, 'Incorrect credentials')
    @ns_deployment.response(403, 'Missing deployment access')
    @ns_deployment.response(404, 'Deployment doesn\'t exist')
    @api.marshal_with(incident_model)
    def get(self, deployment):
        """
                Returns open incidents the user has access to.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_deployment.has_deployment_access(current_user, deployment)
        all_incidents = current_user.get_incidents(deployment.id, open_only=True)
        return all_incidents, 200


@ns_deployment.route('/<int:id>/assigned-incidents')
@ns_deployment.doc(params={'id': 'Deployment ID.'})
@ns_deployment.resolve_object('deployment', lambda kwargs: Deployment.query.get_or_error(kwargs.pop('id')))
class AssignedIncidentsEndpoint(Resource):
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', [incident_model])
    @ns_deployment.response(401, 'Incorrect credentials')
    @ns_deployment.response(403, 'Missing deployment access')
    @ns_deployment.response(404, 'Deployment doesn\'t exist')
    @api.marshal_with(incident_model)
    def get(self, deployment):
        """
                Returns assigned incidents to the current user.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_deployment.has_deployment_access(current_user, deployment)
        all_incidents = current_user.get_incidents(deployment.id, ignore_permissions=True)
        return all_incidents, 200


@ns_deployment.route('/<int:id>/closed-incidents')
@ns_deployment.doc(params={'id': 'Deployment ID.'})
@ns_deployment.resolve_object('deployment', lambda kwargs: Deployment.query.get_or_error(kwargs.pop('id')))
class ClosedIncidentsEndpoint(Resource):
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', [incident_model])
    @ns_deployment.response(401, 'Incorrect credentials')
    @ns_deployment.response(403, 'Missing deployment access')
    @ns_deployment.response(404, 'Deployment doesn\'t exist')
    @api.marshal_with(incident_model)
    def get(self, deployment):
        """
                Returns closed incidents the user has access to.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_deployment.has_deployment_access(current_user, deployment)
        all_incidents = current_user.get_incidents(deployment.id, closed_only=False)
        return all_incidents, 200


@ns_deployment.route('/<int:id>/users')
@ns_deployment.doc(params={'id': 'Deployment ID.'})
@ns_deployment.resolve_object('deployment', lambda kwargs: Deployment.query.get_or_error(kwargs.pop('id')))
class DeploymentUsersEndpoint(Resource):
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', [user_model])
    @ns_deployment.response(401, 'Incorrect credentials')
    @ns_deployment.response(403, 'Missing deployment access')
    @ns_deployment.response(404, 'Deployment doesn\'t exist')
    @api.marshal_with(user_model)
    def get(self, deployment):
        """
                Returns all users with access to the deployment.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_deployment.has_deployment_access(current_user, deployment)
        if not deployment.groups and not deployment.users:
            all_users = User.query.filter_by(status=1).all()
            return all_users, 200
        users = []
        for x in deployment.groups:
            for y in x.users:
                if x not in users and x.status == 1:
                    users.append(y)
        for x in deployment.users:
            if x not in users and x.status == 1:
                users.append(x)
        return users, 200


@ns_deployment.route('/<int:id>/groups')
@ns_deployment.doc(params={'id': 'Deployment ID.'})
@ns_deployment.resolve_object('deployment', lambda kwargs: Deployment.query.get_or_error(kwargs.pop('id')))
class DeploymentGroupsEndpoint(Resource):
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', [group_model])
    @ns_deployment.response(401, 'Incorrect credentials')
    @ns_deployment.response(403, 'Missing deployment access')
    @ns_deployment.response(404, 'Deployment doesn\'t exist')
    @api.marshal_with(group_model)
    def get(self, deployment):
        """
                Returns all groups with access to the deployment.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_deployment.has_deployment_access(current_user, deployment)
        if not deployment.groups and not deployment.users:
            all_groups = Group.query.all()
            return all_groups, 200
        return deployment.groups, 200
