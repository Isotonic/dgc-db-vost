from app.api import c5_api
from sqlalchemy import func
from app.models import User, Deployment
from app.utils.create import new_deployment
from flask_restplus import Resource, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.utils.models import new_deployment_model, deployment_model

ns_deployment = Namespace('Deployment', description='Used to carry out operations related with deployments.',
                          path='/deployment')


@ns_deployment.route('/list')
class get_all_deployments(Resource):
    @jwt_required
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', [deployment_model])
    @ns_deployment.response(404, 'No deployments exist')
    def get(self):
        """
                Returns all deployment.
        """
        all_deployments = [{'id': m.id, 'name': m.name, 'description': m.description, 'open': m.open_status,
                            'created_at': m.created_at, 'groups': [x.id for x in m.groups],
                            'users': [y.id for y in m.users]} for m in Deployment.query.all()]
        if not all_deployments:
            ns_deployment.abort(404, 'No groups exist')
        return all_deployments, 200


@ns_deployment.route('/get/<int:id>')
class get_deployment(Resource):
    @jwt_required
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', [deployment_model])
    @ns_deployment.response(401, "Deployment doen't exist")
    def get(self):
        """
                Returns deployment info.
        """
        payload = c5_api.payload
        deployment = Deployment.query.filter_by(id=id).first()
        if not deployment:
            ns_deployment.abort(401, "Deployment doesn't exist")
        return {'id': deployment.id, 'name': deployment.name, 'description': deployment.description,
                'open': deployment.open_status, 'created_at': deployment.created_at,
                'groups': [m.id for m in deployment.groups], 'users': [m.id for m in deployment.users]}, 200


@ns_deployment.route('/create')
class create_new_deployment(Resource):
    @jwt_required
    @ns_deployment.expect(new_deployment_model, validate=True)
    @ns_deployment.doc(security='access_token')
    @ns_deployment.response(200, 'Success', deployment_model)
    @ns_deployment.response(401, 'Incorrect credentials')
    @ns_deployment.response(403, 'Missing Supervisor permission')
    def post(self):
        """
                Creates a new deployment, requires the Supervisor permission. Supplying a list of groups and users is optional and is left blank if everyone is to have access.
        """
        payload = c5_api.payload
        current_user = User.query.filter_by(username=get_jwt_identity()).first()

        if not current_user.group.has_permission('Supervisor'):
            ns_deployment.abort(403, 'Missing Supervisor permission')

        deployment = Deployment.query.filter(func.lower(Deployment.name) == func.lower(payload['name'])).first()
        if deployment is not None:
            ns_deployment.abort(409, 'Deployment already exists')

        created_deployment = new_deployment(payload['name'], payload['description'], payload['groups'],
                                            payload['users'], current_user)
        return {'id': created_deployment.id, 'name': created_deployment.name,
                'description': created_deployment.description, 'open': created_deployment.open_status,
                'created_at': created_deployment.created_at, 'groups': [m.id for m in created_deployment.groups],
                'users': [m.id for m in created_deployment.users]}, 200