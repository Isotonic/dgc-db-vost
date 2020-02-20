from ..api import api
from .utils.resource import Resource
from .utils.namespace import Namespace
from ..models import User, SupervisorActions
from ..utils.supervisor import mark_request_complete
from flask_jwt_extended import jwt_required, get_jwt_identity
from .utils.models import action_required_model, mark_dealt_with_model

ns_actions_required = Namespace('Actions Required', description='Used to carry out actions related to actions requested.', path='/actions-required', decorators=[jwt_required])

@ns_actions_required.route('/<int:id>')
@ns_actions_required.doc(params={'id': 'Task Comment ID.'})
@ns_actions_required.resolve_object('action_required', lambda kwargs: SupervisorActions.query.get_or_error(kwargs.pop('id')))
class CommentEndpoint(Resource):
    @ns_actions_required.doc(security='access_token')
    @ns_actions_required.response(200, 'Success', [action_required_model])
    @ns_actions_required.response(401, 'Incorrect credentials')
    @ns_actions_required.response(403, 'Missing incident access')
    @ns_actions_required.response(403, 'Missing supervisor permission')
    @ns_actions_required.response(404, 'Requested action doesn\'t exist')
    @api.marshal_with(action_required_model)
    def get(self, action_required):
        """
                Returns action required.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_actions_required.has_permission(current_user, 'supervisor')
        return action_required, 200


    @ns_actions_required.doc(security='access_token')
    @ns_actions_required.expect(mark_dealt_with_model)
    @ns_actions_required.response(200, 'Success')
    @ns_actions_required.response(401, 'Incorrect credentials')
    @ns_actions_required.response(403, 'Missing incident access')
    @ns_actions_required.response(403, 'Missing supervisor permission')
    @ns_actions_required.response(404, 'Requested action doesn\'t exist')
    def put(self, action_required):
        """
                Marks action required as dealt with.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        ns_actions_required.has_permission(current_user, 'supervisor')
        change = False
        if 'carryOutAction' in api.payload.keys() and api.payload['carryOutAction']:
            change =  True
        mark_request_complete(action_required, change, current_user)
        return 'Success', 200
