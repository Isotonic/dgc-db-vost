from app import db
from ..api import api
from flask_restx import marshal
from ..models import User, Incident
from .utils.resource import Resource
from .utils.namespace import Namespace
from ..utils.create import create_comment, create_task
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.change import edit_incident, change_incident_status, change_incident_allocation, change_incident_priority, change_incident_public
from .utils.models import id_model, incident_model, pinned_model, status_model, user_model, priority_model, public_model, comment_model, new_comment_model, task_model, new_task_model, edit_incident_model

ns_incident = Namespace('Incident', description='Used to carry out actions related to incidents.', path='/incidents', decorators=[jwt_required])

def format_incident(incident, user):
    incident_marshalled = marshal(incident, incident_model)
    if user in incident.users_pinned:
        incident_marshalled['pinned'] = True
    else:
        incident_marshalled['pinned'] = False
    return incident_marshalled

@ns_incident.route('/<int:id>')
@ns_incident.doc(params={'id': 'Incident ID.'})
@ns_incident.resolve_object('incident', lambda kwargs: Incident.query.get_or_error(kwargs.pop('id')))
class IncidentEndpoint(Resource):
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', incident_model)
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    def get(self, incident):
        """
                Returns incident info.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        return format_incident(incident, current_user), 200


    @ns_incident.expect(edit_incident_model, validate=True)
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', incident_model)
    @ns_incident.response(400, 'Name is empty')
    @ns_incident.response(400, 'Incident already has these details')
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(401, 'Invalid incident type')
    def put(self, incident):
        """
                Edits incident. Supplying a description, reportedVia and referece are optional and can be omitted.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        if payload['name'] == '':
            ns_incident.abort(400, 'Name is empty')

        if payload['type'] not in Incident.incident_types.keys():
            ns_incident.abort(400, 'Invalid incident type')

        if 'description' in payload.keys():
            description = payload['description']
        else:
            description = None

        if 'reportedVia' in payload.keys():
            reported_via = payload['reportedVia']
        else:
            reported_via = None

        if 'reference' in payload.keys():
            reference = payload['reference']
        else:
            reference = None

        if edit_incident(incident, payload['name'],description, payload['type'], reported_via, reference, current_user) is False:
            ns_deployment.abort(400, 'Incident already has these details')
        return format_incident(incident, current_user), 200


@ns_incident.route('/<int:id>/pinned')
@ns_incident.doc(params={'id': 'Incident ID.'})
@ns_incident.resolve_object('incident', lambda kwargs: Incident.query.get_or_error(kwargs.pop('id')))
class PinnedEndpoint(Resource):
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', [pinned_model])
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(pinned_model)
    def get(self, incident):
        """
                Returns incident's pinned status.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        if current_user.id in incident.users_pinned:
            pinned = {'pinned': True}
        else:
            pinned = {'pinned': False}
        return pinned, 200


    @ns_incident.doc(security='access_token')
    @ns_incident.expect(pinned_model, validate=True)
    @ns_incident.response(200, 'Success', [pinned_model])
    @ns_incident.response(400, 'Incident is already pinned')
    @ns_incident.response(400, 'Incident is already unpinned')
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(pinned_model)
    def post(self, incident):
        """
                Changes an incident's pinned status.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        if api.payload['pinned'] and current_user in incident.users_pinned:
            ns_incident.abort(400, 'Incident is already pinned')
        elif not api.payload['pinned'] and current_user not in incident.users_pinned:
            ns_incident.abort(400, 'Incident is already unpinned')
        elif api.payload['pinned']:
            incident.users_pinned += [current_user]
        else:
            incident.users_pinned.remove(current_user)
        db.session.commit()
        return api.payload, 200


@ns_incident.route('/<int:id>/status')
@ns_incident.doc(params={'id': 'Incident ID.'})
@ns_incident.resolve_object('incident', lambda kwargs: Incident.query.get_or_error(kwargs.pop('id')))
class StatusEndpoint(Resource):
    @ns_incident.doc(security='access_token')
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
    @ns_incident.response(403, 'Missing permission to change incident status')
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
    @ns_incident.expect([id_model], validate=True)
    @ns_incident.response(200, 'Success', [user_model])
    @ns_incident.response(400, 'Input payload validation failed')
    @ns_incident.response(400, 'Incident already has this allocation')
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(403, 'Missing permission to change incident allocation')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(user_model)
    def put(self, incident):
        """
                Changes incident's allocation. Supply a list of user IDs, can be empty.
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
    @ns_incident.response(403, 'Missing permission to change incident priority')
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
class PublicEndpoint(Resource):
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', public_model)
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(public_model)
    def get(self, incident):
        """
                Returns if incident is viewable by the public or not.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        return incident, 200


    @ns_incident.doc(security='access_token')
    @ns_incident.expect(public_model, validate=True)
    @ns_incident.response(200, 'Success', public_model)
    @ns_incident.response(400, 'Incident is already public')
    @ns_incident.response(400, 'Incident is already not public')
    @ns_incident.response(400, 'Input payload validation failed')
    @ns_incident.response(400, 'Name is empty')
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(403, 'Missing permission to change incident viewability')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(public_model)
    def put(self, incident):
        """
                Changes if incident is viewable by the public or not.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        ns_incident.has_permission(current_user, 'mark_as_public')
        if 'name' in api.payload.keys():
            name = api.payload['name']
            if name == '':
                ns_incident.abort(400, 'Name is empty')
        else:
            name = None

        if 'description' in api.payload.keys():
            description = api.payload['description']
        else:
            description = None

        if change_incident_public(incident, api.payload['public'], name, description, current_user) is False:
            ns_incident.abort(400, f'Incident is already {"public" if api.payload["public"] else "not public"}')
        return incident, 200


@ns_incident.route('/<int:id>/comments')
@ns_incident.doc(params={'id': 'Incident ID.'})
@ns_incident.resolve_object('incident', lambda kwargs: Incident.query.get_or_error(kwargs.pop('id')))
class CommentsEndpoint(Resource):
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', comment_model)
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(comment_model)
    def get(self, incident):
        """
                Returns incident's comments.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        return incident.comments, 200


    @ns_incident.doc(security='access_token')
    @ns_incident.expect(new_comment_model, validate=True)
    @ns_incident.response(200, 'Success', comment_model)
    @ns_incident.response(400, 'Input payload validation failed')
    @ns_incident.response(400, 'Text is empty')
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(comment_model)
    def post(self, incident):
        """
                Adds a new comment to the incident.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)

        if current_user.has_permission('mark_as_public') and 'public' in api.payload.keys():
            public = api.payload['public']
        else:
            public = False

        comment = create_comment(api.payload['text'], public, incident, current_user)
        if comment is False:
            ns_incident.abort(400, 'Text is empty')
        return comment, 200


@ns_incident.route('/<int:id>/tasks')
@ns_incident.doc(params={'id': 'Incident ID.'})
@ns_incident.resolve_object('incident', lambda kwargs: Incident.query.get_or_error(kwargs.pop('id')))
class TasksEndpoint(Resource):
    @ns_incident.doc(security='access_token')
    @ns_incident.response(200, 'Success', comment_model)
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(task_model)
    def get(self, incident):
        """
                Returns incident's tasks.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        return incident.tasks, 200


    @ns_incident.doc(security='access_token')
    @ns_incident.expect(new_task_model, validate=True)
    @ns_incident.response(200, 'Success', task_model)
    @ns_incident.response(400, 'Input payload validation failed')
    @ns_incident.response(400, 'Name is empty')
    @ns_incident.response(401, 'Incorrect credentials')
    @ns_incident.response(403, 'Missing incident access')
    @ns_incident.response(404, 'Incident doesn\'t exist')
    @api.marshal_with(task_model)
    def post(self, incident):
        """
                Adds a new task to the incident.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_incident.has_incident_access(current_user, incident)
        users = None
        description = None
        if 'assignedTo' in api.payload.keys():
            users = [m for m in User.query.filter(User.id.in_(api.payload['assignedTo'])).all() if m.has_deployment_access(incident.deployment)]
        if 'description' in api.payload.keys():
            description = api.payload['description']
        task = create_task(api.payload['name'], users, description, incident, current_user)
        if task is False:
            ns_incident.abort(400, 'Name is empty')
        return task, 200

