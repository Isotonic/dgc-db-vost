from ..api import api
from sqlalchemy import or_
from .utils.resource import Resource
from .utils.namespace import Namespace
from datetime import datetime, timedelta
from ..models import Incident, Deployment
from .utils.models import public_incident_model, public_deployment_model

ns_public = Namespace('Public', description='Used to carry out actions related to publicly viewable incidents.', path='/public')

@ns_public.route('/incidents')
class OpenIncidentsEndpoint(Resource):
    @ns_public.response(200, 'Success', [public_incident_model])
    @api.marshal_with(public_incident_model)
    def get(self):
        """
                Returns open incident and incidents closed within the last 72 hours viewable by the public.
        """
        incidents = Incident.query.filter(Incident.public==True, Deployment.open_status==True, or_(Incident.open_status==True, Incident.closed_at>(datetime.utcnow() - timedelta(days=3)))).all()
        return incidents, 200


@ns_public.route('/open-incidents')
class OpenIncidentsEndpoint(Resource):
    @ns_public.response(200, 'Success', [public_incident_model])
    @api.marshal_with(public_incident_model)
    def get(self):
        """
                Returns open incidents viewable by the public.
        """
        incidents = Incident.query.filter(Incident.open_status==True, Deployment.open_status==True, Incident.public==True).all()
        return incidents, 200


@ns_public.route('/closed-incidents')
class ClosedIncidentsEndpoint(Resource):
    @ns_public.response(200, 'Success', [public_incident_model])
    @api.marshal_with(public_incident_model)
    def get(self):
        """
                Returns incidents closed within the last 72 hours viewable by the public.
        """
        incidents = Incident.query.filter(Incident.open_status==False, Deployment.open_status==True, Incident.public==True, Incident.closed_at>(datetime.utcnow() - timedelta(days=3))).all()
        return incidents, 200


@ns_public.route('/incident/<int:id>')
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
        if incident.public and incident.deployment.open_status:
            return incident, 200
        ns_public.abort(400, 'Incident doesn\'t exist')


@ns_public.route('/deployments')
class DeploymentsEndpoint(Resource):
    @ns_public.response(200, 'Success', [public_deployment_model])
    @ns_public.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(public_deployment_model)
    def get(self):
        """
                Returns open deployments.
        """
        deployments = Deployment.query.filter_by(open_status=True).all()
        return deployments, 200
