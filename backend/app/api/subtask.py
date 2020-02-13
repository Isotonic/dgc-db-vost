from ..api import api
from .utils.resource import Resource
from .utils.namespace import Namespace
from ..utils.delete import delete_subtask
from ..models import User, IncidentSubTask
from ..utils.change import change_subtask_status, change_subtask
from flask_jwt_extended import jwt_required, get_jwt_identity
from .utils.models import subtask_model, completion_model, subtask_edited_model

ns_subtask = Namespace('Subtask', description='Used to carry out actions related to subtasks.', path='/subtasks', decorators=[jwt_required])

@ns_subtask.route('/<int:id>')
@ns_subtask.doc(params={'id': 'Subtask ID.'})
@ns_subtask.resolve_object('subtask', lambda kwargs: IncidentSubTask.query.get_or_error(kwargs.pop('id')))
class SubtaskEndpoint(Resource):
    @ns_subtask.doc(security='access_token')
    @ns_subtask.response(200, 'Success', [subtask_model])
    @ns_subtask.response(401, 'Incorrect credentials')
    @ns_subtask.response(403, 'Missing incident access')
    @ns_subtask.response(404, 'Subtask doesn\'t exist')
    @api.marshal_with(subtask_model)
    def get(self, subtask):
        """
                Returns subtask info.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_subtask.has_incident_access(current_user, subtask.task.incident)
        return subtask, 200


    @ns_subtask.doc(security='access_token')
    @ns_subtask.expect(subtask_edited_model, validate=True)
    @ns_subtask.response(200, 'Success', [subtask_model])
    @ns_subtask.response(400, 'Subtask already has this data')
    @ns_subtask.response(401, 'Incorrect credentials')
    @ns_subtask.response(403, 'Missing incident access')
    @ns_subtask.response(404, 'Subtask doesn\'t exist')
    @api.marshal_with(subtask_model)
    def put(self, subtask):
        """
                Edits subtask.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_subtask.has_incident_access(current_user, subtask.task.incident)
        users = [m for m in User.query.filter(User.id.in_(api.payload['assignedTo'])).all() if m.has_deployment_access(subtask.task.incident.deployment)]
        if change_subtask(subtask, api.payload['name'], users, current_user) is False:
            ns_subtask.abort(400, 'Subtask already has this data')
        return subtask, 200


    @ns_subtask.doc(security='access_token')
    @ns_subtask.response(200, 'Success')
    @ns_subtask.response(401, 'Incorrect credentials')
    @ns_subtask.response(403, 'Missing incident access')
    @ns_subtask.response(404, 'Subtask doesn\'t exist')
    def delete(self, subtask):
        """
                Deletes subtask.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_subtask.has_incident_access(current_user, subtask.task.incident)
        delete_subtask(subtask, current_user)


@ns_subtask.route('/<int:id>/status')
@ns_subtask.doc(params={'id': 'Subtask ID.'})
@ns_subtask.resolve_object('subtask', lambda kwargs: IncidentSubTask.query.get_or_error(kwargs.pop('id')))
class StatusEndpoint(Resource):
    @ns_subtask.doc(security='access_token')
    @ns_subtask.response(200, 'Success', completion_model)
    @ns_subtask.response(401, 'Incorrect credentials')
    @ns_subtask.response(403, 'Missing incident access')
    @ns_subtask.response(404, 'Subtask doesn\'t exist')
    @api.marshal_with(completion_model)
    def get(self, subtask):
        """
                Returns subtask's status.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_subtask.has_incident_access(current_user, subtask.task.incident)
        return subtask, 200


    @ns_subtask.doc(security='access_token')
    @ns_subtask.expect(completion_model, validate=True)
    @ns_subtask.response(200, 'Success', completion_model)
    @ns_subtask.response(400, 'Subtask already has this status')
    @ns_subtask.response(401, 'Incorrect credentials')
    @ns_subtask.response(403, 'Missing incident access')
    @ns_subtask.response(404, 'Subtask doesn\'t exist')
    @api.marshal_with(completion_model)
    def put(self, subtask):
        """
                Changes subtask's status.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_subtask.has_incident_access(current_user, subtask.task.incident)
        if change_subtask_status(subtask, api.payload['completed'], current_user) is False:
            ns_subtask.abort(400, 'Subtask already has this status')
        return subtask, 200
