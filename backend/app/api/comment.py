from ..api import api
from .utils.resource import Resource
from .utils.namespace import Namespace
from ..utils.delete import delete_comment
from ..models import User, IncidentComment
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.change import change_comment_text, change_comment_public
from .utils.models import comment_model, public_model, text_model, comment_edited_model

ns_comment = Namespace('Comment', description='Used to carry out actions related to comments.', path='/comments', decorators=[jwt_required])

@ns_comment.route('/<int:id>')
@ns_comment.doc(params={'id': 'Comment ID.'})
@ns_comment.resolve_object('comment', lambda kwargs: IncidentComment.query.get_or_error(kwargs.pop('id')))
class CommentEndpoint(Resource):
    @ns_comment.doc(security='access_token')
    @ns_comment.response(200, 'Success', [comment_model])
    @ns_comment.response(401, 'Incorrect credentials')
    @ns_comment.response(403, 'Missing incident access')
    @ns_comment.response(404, 'Comment doesn\'t exist')
    @api.marshal_with(comment_model)
    def get(self, comment):
        """
                Returns task comment.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_comment.has_incident_access(current_user, comment.incident)
        return comment, 200


    @ns_comment.doc(security='access_token')
    @ns_comment.expect(text_model, validate=True)
    @ns_comment.response(200, 'Success', [text_model])
    @ns_comment.response(400, 'Comment already has this text')
    @ns_comment.response(401, 'Incorrect credentials')
    @ns_comment.response(403, 'Missing incident access')
    @ns_comment.response(403, 'Missing permission, not your comment')
    @ns_comment.response(404, 'Comment doesn\'t exist')
    @api.marshal_with(comment_edited_model)
    def put(self, comment):
        """
                Updates comment text.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_comment.has_incident_access(current_user, comment.incident)
        if comment.user_id != current_user.id:
            ns_comment.abort(403, 'Missing permission, not your comment')
        if change_comment_text(comment, api.payload['text'], current_user) is False:
            ns_comment.abort(400, 'Comment already has this text')
        return comment, 200


    @ns_comment.doc(security='access_token')
    @ns_comment.response(200, 'Success')
    @ns_comment.response(401, 'Incorrect credentials')
    @ns_comment.response(403, 'Missing incident access')
    @ns_comment.response(404, 'Comment doesn\'t exist')
    def delete(self, comment):
        """
                Deletes comment.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_comment.has_incident_access(current_user, comment.incident)
        delete_comment(comment, current_user)
        return 'Success', 200
