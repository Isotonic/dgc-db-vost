from ..api import api
from .utils.resource import Resource
from ..utils.delete import delete_task
from .utils.namespace import Namespace
from ..models import User, IncidentTask
from ..utils.create import create_task_comment, create_subtask
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.change import change_task_status, change_task_description, change_task_tags, change_task_assigned
from .utils.models import id_model, task_model, completion_model, user_model, task_comment_model, text_model, tags_model, new_subtask_model, subtask_model

ns_task = Namespace('Task', description='Used to carry out actions related to tasks.', path='/tasks', decorators=[jwt_required])

@ns_task.route('/<int:id>')
@ns_task.doc(params={'id': 'Task ID.'})
@ns_task.resolve_object('task', lambda kwargs: IncidentTask.query.get_or_error(kwargs.pop('id')))
class TaskEndpoint(Resource):
    @ns_task.doc(security='access_token')
    @ns_task.response(200, 'Success', [task_model])
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Task doesn\'t exist')
    @api.marshal_with(task_model)
    def get(self, task):
        """
                Returns task info.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        return task, 200


    @ns_task.doc(security='access_token')
    @ns_task.response(200, 'Success')
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Task doesn\'t exist')
    def delete(self, task):
        """
                Deletes task
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        return delete_task(task, current_user)


@ns_task.route('/<int:id>/status')
@ns_task.doc(params={'id': 'Task ID.'})
@ns_task.resolve_object('task', lambda kwargs: IncidentTask.query.get_or_error(kwargs.pop('id')))
class StatusEndpoint(Resource):
    @ns_task.doc(security='access_token')
    @ns_task.response(200, 'Success', completion_model)
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Task doesn\'t exist')
    @api.marshal_with(completion_model)
    def get(self, task):
        """
                Returns task's status.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        return task, 200


    @ns_task.doc(security='access_token')
    @ns_task.expect(completion_model, validate=True)
    @ns_task.response(200, 'Success', completion_model)
    @ns_task.response(400, 'Task already has this status')
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Task doesn\'t exist')
    @api.marshal_with(completion_model)
    def put(self, task):
        """
                Changes a task's status.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        if change_task_status(task, api.payload['completed'], current_user) is False:
            ns_task.abort(400, 'Task already has this status')
        return task, 200


@ns_task.route('/<int:id>/description')
@ns_task.doc(params={'id': 'Task ID.'})
@ns_task.resolve_object('task', lambda kwargs: IncidentTask.query.get_or_error(kwargs.pop('id')))
class DescriptionEndpoint(Resource):
    @ns_task.doc(security='access_token')
    @ns_task.response(200, 'Success', text_model)
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Task doesn\'t exist')
    @api.marshal_with(text_model)
    def get(self, task):
        """
                Returns task's description.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        return task.description, 200


    @ns_task.doc(security='access_token')
    @ns_task.expect(text_model, validate=True)
    @ns_task.response(200, 'Success', text_model)
    @ns_task.response(400, 'Task already has this status')
    @ns_task.response(400, 'Text is empty')
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(403, 'Missing permission')
    @ns_task.response(404, 'Task doesn\'t exist')
    @api.marshal_with(text_model)
    def put(self, task):
        """
                Changes a task's description.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        if change_task_description(task, api.payload['text'], current_user) is False:
            ns_task.abort(400, 'Task already has this description')
        return task, 200


@ns_task.route('/<int:id>/tags')
@ns_task.doc(params={'id': 'Task ID.'})
@ns_task.resolve_object('task', lambda kwargs: IncidentTask.query.get_or_error(kwargs.pop('id')))
class TagsEndpoint(Resource):
    @ns_task.doc(security='access_token')
    @ns_task.response(200, 'Success', [tags_model])
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Task doesn\'t exist')
    @api.marshal_with(tags_model)
    def get(self, task):
        """
                Returns task's assigned users.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        return task, 200


    @ns_task.doc(security='access_token')
    @ns_task.expect(tags_model, validate=True)
    @ns_task.response(200, 'Success', tags_model)
    @ns_task.response(400, 'Task already has these tags')
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Task doesn\'t exist')
    @api.marshal_with(tags_model)
    def put(self, task):
        """
                Changes task's assigned users. Supply a list of user IDs, can be empty.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        if change_task_tags(task, api.payload['tags'], current_user) is False:
            ns_task.abort(400, 'Task already had these tags')
        return task, 200


@ns_task.route('/<int:id>/assigned')
@ns_task.doc(params={'id': 'Task ID.'})
@ns_task.resolve_object('task', lambda kwargs: IncidentTask.query.get_or_error(kwargs.pop('id')))
class AssignedEndpoint(Resource):
    @ns_task.doc(security='access_token')
    @ns_task.response(200, 'Success', [user_model])
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Task doesn\'t exist')
    @api.marshal_with(user_model)
    def get(self, task):
        """
                Returns task's assigned users.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        return task.assigned_to, 200


    @ns_task.doc(security='access_token')
    @ns_task.expect([id_model], validate=True)
    @ns_task.response(200, 'Success', [user_model])
    @ns_task.response(400, 'Task already has this allocation')
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Task doesn\'t exist')
    @api.marshal_with(user_model)
    def put(self, task):
        """
                Changes task's assigned users. Supply a list of user IDs, can be empty.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        users = [m for m in User.query.filter(User.id.in_(api.payload['users'])).all() if m.has_deployment_access(task.incident.deployment)]
        if change_task_assigned(task, users, current_user) is False:
            ns_task.abort(400, 'Task already has this allocation')
        return task.assigned_to, 200


@ns_task.route('/<int:id>/comments')
@ns_task.doc(params={'id': 'Task ID.'})
@ns_task.resolve_object('task', lambda kwargs: IncidentTask.query.get_or_error(kwargs.pop('id')))
class CommentsEndpoint(Resource):
    @ns_task.doc(security='access_token')
    @ns_task.response(200, 'Success', [task_comment_model])
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Task doesn\'t exist')
    @api.marshal_with(task_comment_model)
    def get(self, task):
        """
                Returns task's comments.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        return task.comments, 200


    @ns_task.doc(security='access_token')
    @ns_task.expect(text_model, validate=True)
    @ns_task.response(200, 'Success', [task_comment_model])
    @ns_task.response(400, 'Text is empty')
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Task doesn\'t exist')
    @api.marshal_with(task_comment_model)
    def post(self, task):
        """
                Create a task comment.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        comment = create_task_comment(api.payload['text'], task, current_user)
        if comment is False:
            ns_task.abort(400, 'Text is empty')
        return comment, 200


@ns_task.route('/<int:id>/subtasks')
@ns_task.doc(params={'id': 'Task ID.'})
@ns_task.resolve_object('task', lambda kwargs: IncidentTask.query.get_or_error(kwargs.pop('id')))
class CommentsEndpoint(Resource):
    @ns_task.doc(security='access_token')
    @ns_task.response(200, 'Success', [subtask_model])
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Task doesn\'t exist')
    @api.marshal_with(subtask_model)
    def get(self, task):
        """
                Returns task's subtasks.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        return task.subtasks, 200


    @ns_task.doc(security='access_token')
    @ns_task.expect(new_subtask_model, validate=True)
    @ns_task.response(200, 'Success', [subtask_model])
    @ns_task.response(400, 'Text is empty')
    @ns_task.response(401, 'Incorrect credentials')
    @ns_task.response(403, 'Missing incident access')
    @ns_task.response(404, 'Name doesn\'t exist')
    @api.marshal_with(subtask_model)
    def post(self, task):
        """
                Create a task subtask.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task.has_incident_access(current_user, task.incident)
        users = []
        if 'assignedTo' in api.payload.keys():
            users = [m for m in User.query.filter(User.id.in_(api.payload['assignedTo'])).all() if m.has_deployment_access(task.incident.deployment)]
        subtask = create_subtask(api.payload['name'], users, task, current_user)
        if subtask is False:
            ns_task.abort(400, 'Name is empty')
        return subtask, 200
