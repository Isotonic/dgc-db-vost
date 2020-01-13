from app.api import api
from app.api.utils.resource import Resource
from app.api.utils.namespace import Namespace
from app.models import User, Incident, Deployment
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.utils.models import new_incident_model, incident_model, point_feature_model

ns_incident = Namespace('Incident', description='Used to carry out operations related to incidents.', path='/incident')

@ns_incident.route('/<int:id>')
@ns_incident.doc(params={'id': 'Incident ID.'})
@ns_incident.resolve_object('incident', lambda kwargs: Incident.query.get_or_error(kwargs.pop('id')))
class GetIncident(Resource):
    @jwt_required
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', [incident_model])
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(incident_model)
    def get(self, incident):
        """
                Returns incident info.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        return incident, 200


@ns_incident.route('/<int:id>/status')
@ns_incident.doc(params={'id': 'Incident ID.'})
@ns_incident.resolve_object('incident', lambda kwargs: Incident.query.get_or_error(kwargs.pop('id')))
class ChangeIncidentStatus(Resource):
    @jwt_required
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', [incident_model])
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(incident_model)
    def post(self, incident):
        """
                Changes an incident's status.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident) ##TODO
        return incident, 200
