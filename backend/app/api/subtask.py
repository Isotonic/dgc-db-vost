from ..api import api
from .utils.resource import Resource
from .utils.namespace import Namespace
from ..models import User, IncidentSubTask
from flask_jwt_extended import jwt_required, get_jwt_identity
from .utils.models import subtask_model, completion_model
from ..utils.delete import delete_subtask
from ..utils.change import change_subtask_status

ns_subtask = Namespace('Subtask', description='Used to carry out operations related to subtasks.', path='/subtasks', decorators=[jwt_required])

@ns_subtask.route('/<int:id>')
@ns_subtask.doc(params={'id': 'Subtask ID.'})
@ns_subtask.resolve_object('subtask', lambda kwargs: IncidentSubTask.query.get_or_error(kwargs.pop('id')))
class GetSubtask(Resource):
    @ns_subtask.doc(security='access_token')
    @ns_subtask.response(200, 'Success', [subtask_model])
    @ns_subtask.response(401, 'Incorrect credentials')
    @ns_subtask.response(403, 'Missing incident access')
    @ns_subtask.response(404, 'Task doesn\'t exist')
    @api.marshal_with(subtask_model)
    def get(self, subtask):
        """
                Returns subtask info.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_subtask.has_incident_access(current_user, subtask.task.incident)
        return subtask, 200


    @ns_subtask.doc(security='access_token')
    @ns_subtask.response(200, 'Success')
    @ns_subtask.response(401, 'Incorrect credentials')
    @ns_subtask.response(403, 'Missing incident access')
    @ns_subtask.response(404, 'Task doesn\'t exist')
    @api.marshal_with(subtask_model)
    def delete(self, subtask):
        """
                Returns subtask info.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_subtask.has_incident_access(current_user, subtask.task.incident)
        delete_subtask(subtask, current_user)


@ns_subtask.route('/<int:id>/status')
@ns_subtask.doc(params={'id': 'Subtask ID.'})
@ns_subtask.resolve_object('subtask', lambda kwargs: IncidentSubTask.query.get_or_error(kwargs.pop('id')))
class ChangeSubtaskStatus(Resource):
    @ns_subtask.doc(security='access_token')
    @ns_subtask.expect(completion_model, validate=True)
    @ns_subtask.response(200, 'Success', completion_model)
    @ns_subtask.response(401, 'Incorrect credentials')
    @ns_subtask.response(400, 'Subtask already has this status')
    @ns_subtask.response(403, 'Missing incident access')
    @ns_subtask.response(403, 'Missing permission')
    @ns_subtask.response(404, 'Task doesn\'t exist')
    @api.marshal_with(completion_model)
    def put(self, subtask):
        """
                Changes a subtask's status.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_subtask.has_incident_access(current_user, subtask.task.incident)
        if change_subtask_status(subtask, api.payload['completed'], current_user) is False:
            ns_subtask.abort(400, 'Subtask already has this status')
        return subtask, 200
