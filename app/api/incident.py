from app.api import c5_api
from app.models import User, Incident
from app.utils.create import new_incident
from flask_restplus import Resource, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.utils.models import new_incident_model, incident_model

ns_incident = Namespace('Incident', description='Used to carry out operations related with incidents.',
                        path='/incident')


@ns_incident.route('/list')
class get_all_incidents(Resource):
    @jwt_required
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', [incident_model])
    @ns_incident.response(404, 'No incidents exist')
    def get(self):
        """
                Returns all incidents.
        """
        all_incidents = [{'id': m.id, 'name': m.name, 'description': m.description,
                          'location': m.location, 'open': m.open_status, 'public': m.public,
                          'flagged': m.flagged, 'type': m.incident_type, 'priority': m.priority,
                          'xcoord': m.xcoord, 'ycoord': m.ycoord,
                          'created_at': m.created_at} for m in Incident.query.all()]
        if not all_incidents:
            ns_incident.abort(404, 'No users exist')
        return all_incidents, 200


@ns_incident.route('/get/<int:id>')
class get_incident(Resource):
    @jwt_required
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', [incident_model])
    @ns_incident.response(401, "Incident doesn't exist")
    def get(self, id):
        """
                Returns incident info.
        """
        payload = c5_api.payload
        incident = Incident.query.filter_by(id=id).first()
        if not incident:
            ns_incident.abort(401, "Incident doesn't exist")
        return {'id': incident.id, 'name': incident.name, 'description': incident.description,
                'location': incident.location, 'open': incident.open_status, 'public': incident.public,
                'flagged': incident.flagged, 'type': incident.incident_type, 'priority': incident.priority,
                'xcoord': incident.xcoord, 'ycoord': incident.ycoord,
                'created_at': incident.created_at}, 200


@ns_incident.route('/create')
class create_new_incident(Resource):
    @jwt_required
    @ns_incident.expect(new_incident_model, validate=True)
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', incident_model)
    @ns_incident.response(401, 'Incorrect credentials')
    def post(self):
        """
                Creates a new incident.
        """
        payload = c5_api.payload
        current_user = User.query.filter_by(username=get_jwt_identity()).first()

        created_incident = new_incident(payload['name'], payload['description'], payload['location'], current_user)
        return {'id': created_incident.id, 'name': created_incident.name, 'description': created_incident.description,
                'location': created_incident.location, 'open': created_incident.open_status,
                'public': created_incident.public,
                'flagged': created_incident.flagged, 'type': created_incident.incident_type,
                'priority': created_incident.priority,
                'xcoord': created_incident.xcoord, 'ycoord': created_incident.ycoord,
                'created_at': created_incident.created_at}, 200
