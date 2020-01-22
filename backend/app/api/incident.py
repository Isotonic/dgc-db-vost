from ..api import api
from ..models import User, Incident
from .utils.resource import Resource
from .utils.namespace import Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from .utils.models import id_model, incident_model, status_model, user_model, priority_model, public_model
from ..utils.change import change_incident_status, change_incident_allocation, change_incident_priority, change_incident_public

ns_incident = Namespace('Incident', description='Used to carry out actions related to incidents.', path='/incidents', decorators=[jwt_required])

@ns_incident.route('/<int:id>')
@ns_incident.doc(params={'id': 'Incident ID.'})
@ns_incident.resolve_object('incident', lambda kwargs: Incident.query.get_or_error(kwargs.pop('id')))
class IncidentEndpoint(Resource):
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', incident_model)
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
class StatusEndpoint(Resource):
    @ns_incident.doc(security='access_token')
    @ns_incident.expect(status_model, validate=True)
    @ns_incident.response(200, 'Success', status_model)
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(status_model)
    def put(self, incident):
        """
                Retuns incident's status.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        return incident, 200


    @ns_incident.doc(security='access_token')
    @ns_incident.expect(status_model, validate=True)
    @ns_incident.response(200, 'Success', status_model)
    @ns_incident.response(400, 'Input payload validation failed')
    @ns_incident.response(400, 'Incident already has this status')
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(403, 'Missing permission')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(status_model)
    def put(self, incident):
        """
                Changes incident's status.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        ns_incident.has_permission(current_user, 'change_status')
        if change_incident_status(incident, api.payload['open'], current_user) is False:
            ns_incident.abort(400, 'Incident already has this status')
        return incident, 200


@ns_incident.route('/<int:id>/allocation')
@ns_incident.doc(params={'id': 'Incident ID.'})
@ns_incident.resolve_object('incident', lambda kwargs: Incident.query.get_or_error(kwargs.pop('id')))
class AllocationEndpoint(Resource):
    @ns_incident.doc(security='access_token')
    @ns_incident.expect(id_model, validate=True)
    @ns_incident.response(200, 'Success', [user_model])
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(user_model)
    def get(self, incident):
        """
                Returns incident's allocation.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        return incident.assigned_to, 200


    @ns_incident.doc(security='access_token')
    @ns_incident.expect(id_model, validate=True)
    @ns_incident.response(200, 'Success', [user_model])
    @ns_incident.response(400, 'Input payload validation failed')
    @ns_incident.response(400, 'Incident already has this allocation')
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(403, 'Missing permission')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(user_model)
    def put(self, incident):
        """
                Changes incident's allocation.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        ns_incident.has_permission(current_user, 'change_allocation')
        users = [m for m in User.query.filter(User.id.in_(api.payload['users'])).all() if m.has_deployment_access(incident.deployment)]
        if change_incident_allocation(incident, users, current_user) is False:
            ns_incident.abort(400, 'Incident already has this allocation')
        return incident.assigned_to, 200


@ns_incident.route('/<int:id>/priority')
@ns_incident.doc(params={'id': 'Incident ID.'})
@ns_incident.resolve_object('incident', lambda kwargs: Incident.query.get_or_error(kwargs.pop('id')))
class PriorityEndpoint(Resource):
    @ns_incident.doc(security='access_token')
    @ns_incident.expect(priority_model, validate=True)
    @ns_incident.response(200, 'Success', priority_model)
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(priority_model)
    def get(self, incident):
        """
                Returns incident's priority.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        return incident, 200


    @ns_incident.doc(security='access_token')
    @ns_incident.expect(priority_model, validate=True)
    @ns_incident.response(200, 'Success', priority_model)
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(400, 'Input payload validation failed')
    @ns_incident.response(400, 'Incident already has this priority')
    @ns_incident.response(401, 'Invalid priority')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(403, 'Missing permission')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(priority_model)
    def put(self, incident):
        """
                Changes incident's priority.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        ns_incident.has_permission(current_user, 'change_status')
        if not api.payload['priority'].lower() in ['standard', 'prompt', 'immediate']:
            ns_incident.abort(401, 'Invalid priority')
        if change_incident_priority(incident, api.payload['priority'], current_user) is False:
            ns_incident.abort(400, 'Incident already has this priority')
        return incident, 200


@ns_incident.route('/<int:id>/public')
@ns_incident.doc(params={'id': 'Incident ID.'})
@ns_incident.resolve_object('incident', lambda kwargs: Incident.query.get_or_error(kwargs.pop('id')))
class Public(Resource):
    @ns_incident.doc(security='access_token')
    @ns_incident.expect(public_model, validate=True)
    @ns_incident.response(200, 'Success', public_model)
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(public_model)
    def get(self, incident):
        """
                Returns if an incident is viewable by the public or not.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        return incident, 200


    @ns_incident.doc(security='access_token')
    @ns_incident.expect(public_model, validate=True)
    @ns_incident.response(200, 'Success', public_model)
    @ns_incident.response(400, 'Incident already has this priority')
    @ns_incident.response(400, 'Input payload validation failed')
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(403, 'Missing permission')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(public_model)
    def put(self, incident):
        """
                Changes if an incident is viewable by the public or not.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        ns_incident.has_permission(current_user, 'mark_as_public')
        if change_incident_public(incident, api.payload['public'], current_user) is False:
            ns_incident.abort(400, f'Incident already is {"public" if api.payload["public"] else "not public"}')
        return incident, 200
