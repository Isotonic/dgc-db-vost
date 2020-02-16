from ..api import api
from ..models import Incident
from .utils.resource import Resource
from .utils.namespace import Namespace
from datetime import datetime, timedelta
from .utils.models import public_incident_model

ns_public = Namespace('Public', description='Used to carry out actions related to publicly viewable incidents.', path='/public')

@ns_public.route('/open-incidents')
class OpenIncidentsEndpoint(Resource):
    @ns_public.response(200, 'Success', [public_incident_model])
    @api.marshal_with(public_incident_model)
    def get(self):
        """
                Returns open incidents viewable by the public.
        """
        incidents = Incident.query.filter(Incident.open_status==True, Incident.public==True).all()
        return incidents, 200


@ns_public.route('/closed-incidents')
class ClosedIncidentsEndpoint(Resource):
    @ns_public.response(200, 'Success', [public_incident_model])
    @api.marshal_with(public_incident_model)
    def get(self):
        """
                Returns incidents closed within the last 24 hours viewable by the public.
        """
        incidents = Incident.query.filter(Incident.open_status==False, Incident.public==True, Incident.closed_at>(datetime.utcnow() - timedelta(days=1))).all()
        return incidents, 200


@ns_public.route('/incidents/<int:id>')
@ns_public.doc(params={'id': 'Incident ID.'})
@ns_public.resolve_object('incident', lambda kwargs: Incident.query.get_or_error(kwargs.pop('id')))
class IncidentEndpoint(Resource):
    @ns_public.response(200, 'Success', [public_incident_model])
    @ns_public.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(public_incident_model)
    def get(self, incident):
        """
                Returns incident.
        """
        return incident, 200
