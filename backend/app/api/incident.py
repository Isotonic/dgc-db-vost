from app.api import dgvost_api
from app.utils.create import create_incident
from flask_restplus import Resource, Namespace
from app.models import User, Incident, Deployment
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.utils.models import new_incident_model, incident_model

ns_incident = Namespace('Incident', description='Used to carry out operations related with incidents.',
                        path='/incident')


@ns_incident.route('/<int:deployment_id>/list')
class GetAllIncidents(Resource):
    @jwt_required
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', [incident_model])
    @ns_incident.response(404, 'Deployment doesn\'t exist')
    def get(self, deployment_id):
        """
                Returns all incidents the user has access to.
        """
        if not Deployment.query.filter_by(id=deployment_id).first():
            ns_incident.abort(404, 'Deployment doesn\'t exist')
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        all_incidents = [{'id': m.id, 'name': m.name, 'description': m.description,
                          'location': m.location, 'open': m.open_status, 'public': m.public,
                          'flagged': m.flagged, 'type': m.incident_type, 'priority': m.priority,
                          'longitude': m.longitude, 'latitude': m.latitude,
                          'created_at': m.created_at.timestamp()} for m in current_user.get_incidents(deployment_id)]
        return all_incidents, 200


@ns_incident.route('/<int:deployment_id>/get/<int:incident_id>')
class GetIncident(Resource):
    @jwt_required
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', [incident_model])
    @ns_incident.response(401, 'Incident doesn\'t exist')
    def get(self, deployment_id, incident_id):
        """
                Returns incident info.
        """
        incident = Incident.query.filter(Deployment.id==deployment_id, id==incident_id).first()
        if not incident:
            ns_incident.abort(401, 'Incident doesn\'t exist')
        return {'id': incident.id, 'name': incident.name, 'description': incident.description,
                'location': incident.location, 'open': incident.open_status, 'public': incident.public,
                'flagged': incident.flagged, 'type': incident.incident_type, 'priority': incident.priority,
                'longitude': incident.longitude, 'latitude': incident.latitude,
                'created_at': incident.created_at.timestamp()}, 200


@ns_incident.route('/<int:deployment_id>/create')
class CreateNewIncident(Resource):
    @jwt_required
    @ns_incident.expect(new_incident_model, validate=True)
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', incident_model)
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(404, 'Deployment doesn\'t exist')
    def post(self, deployment_id):
        """
                Creates a new incident.
        """
        deployment = Deployment.query.filter_by(id=deployment_id).first()
        if not deployment:
            ns_incident.abort(404, 'Deployment doesn\'t exist')
        payload = dgvost_api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        created_incident = create_incident(payload['name'], payload['description'], payload['location'], payload['reported_via'], payload['reference'], deployment, current_user)
        return {'id': created_incident.id, 'name': created_incident.name, 'description': created_incident.description,
                'location': created_incident.location, 'open': created_incident.open_status,
                'public': created_incident.public,
                'flagged': created_incident.flagged, 'type': created_incident.incident_type,
                'priority': created_incident.priority,
                'longitude': created_incident.longitude, 'latitude': created_incident.latitude,
                'created_at': created_incident.created_at.timestamp()}, 200
