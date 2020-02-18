from ..api import api
from .utils.resource import Resource
from ..models import User, TaskComment
from .utils.namespace import Namespace
from ..utils.delete import delete_task_comment
from ..utils.change import change_task_comment_text
from flask_jwt_extended import jwt_required, get_jwt_identity
from .utils.models import task_comment_model, text_model, comment_edited_model

ns_task_comment = Namespace('Task Comment', description='Used to carry out actions related to comments.', path='/task-comments', decorators=[jwt_required])

@ns_task_comment.route('/<int:id>')
@ns_task_comment.doc(params={'id': 'Task Comment ID.'})
@ns_task_comment.resolve_object('task_comment', lambda kwargs: TaskComment.query.get_or_error(kwargs.pop('id')))
class CommentEndpoint(Resource):
    @ns_task_comment.doc(security='access_token')
    @ns_task_comment.response(200, 'Success', [task_comment_model])
    @ns_task_comment.response(401, 'Incorrect credentials')
    @ns_task_comment.response(403, 'Missing incident access')
    @ns_task_comment.response(404, 'Comment doesn\'t exist')
    @api.marshal_with(task_comment_model)
    def get(self, task_comment):
        """
                Returns comment.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task_comment.has_incident_access(current_user, task_comment.task.incident)
        return task_comment, 200


    @ns_task_comment.doc(security='access_token')
    @ns_task_comment.expect(text_model, validate=True)
    @ns_task_comment.response(200, 'Success', [text_model])
    @ns_task_comment.response(400, 'Comment already has this text')
    @ns_task_comment.response(401, 'Incorrect credentials')
    @ns_task_comment.response(403, 'Missing incident access')
    @ns_task_comment.response(403, 'Missing permission, not your comment')
    @ns_task_comment.response(404, 'Comment doesn\'t exist')
    @api.marshal_with(comment_edited_model)
    def put(self, task_comment):
        """
                Updates comment text.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        task = task_comment.task
        ns_task_comment.has_incident_access(current_user, task.incident)
        if task_comment.user_id != current_user.id:
            ns_task_comment.abort(403, 'Missing permission, not your comment')
        if change_task_comment_text(task_comment, api.payload['text'], current_user) is False:
            ns_task_comment.abort(400, 'Comment already has this text')
        return task_comment, 200


    @ns_task_comment.doc(security='access_token')
    @ns_task_comment.response(200, 'Success')
    @ns_task_comment.response(401, 'Incorrect credentials')
    @ns_task_comment.response(403, 'Missing incident access')
    @ns_task_comment.response(404, 'Comment doesn\'t exist')
    def delete(self, task_comment):
        """
                Deletes subtask.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_task_comment.has_incident_access(current_user, task_comment.task.incident)
        delete_task_comment(task_comment, current_user)
        return 'Success', 200
