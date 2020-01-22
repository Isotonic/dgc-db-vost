from ..api import api
from ..models import Incident
from .utils.resource import Resource
from .utils.namespace import Namespace
from .utils.models import incident_model

ns_public = Namespace('Public', description='Used to carry out actions related to publicly viewable incidents.', path='/public')

@ns_public.route('/open-incidents')
class IncidentsEndpoint(Resource):
    @ns_public.response(200, 'Success', [incident_model])
    @api.marshal_with(incident_model)
    def get(self):
        """
                Returns open incidents viewable by the public.
        """
        incidents = Incident.query.filter(Incident.open_status==True, Incident.public==True).all()
        return incidents, 200
