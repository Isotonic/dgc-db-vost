from ..api import api
from sqlalchemy import func
from ..models import User, Group
from .utils.resource import Resource
from .utils.namespace import Namespace
from ..utils.create import create_group
from .utils.models import new_group_model, group_model
from flask_jwt_extended import jwt_required, get_jwt_identity

ns_group = Namespace('Group', description='Used to carry out operations related to groups.', path='/groups', decorators=[jwt_required])


@ns_group.route('')
class AllGroups(Resource):
    @ns_group.doc(security='access_token')
    @ns_group.response(200, 'Success', [group_model])
    @ns_group.response(401, 'Incorrect credentials')
    @api.marshal_with(group_model)
    def get(self):
        """
                Returns all groups.
        """
        all_groups = Group.query.all()
        return all_groups, 200


    @ns_group.expect(new_group_model, validate=True)
    @ns_group.doc(security='access_token')
    @ns_group.response(200, 'Success', group_model)
    @ns_group.response(401, 'Incorrect credentials')
    @ns_group.response(403, 'Missing Supervisor permission')
    @api.marshal_with(group_model)
    def post(self):
        """
                Creates a new group, requires the Supervisor permission. Supplying a list of permissions is optional.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        ns_group.has_permission(current_user, 'supervisor')

        group = Group.query.filter(func.lower(Group.name) == func.lower(payload['name'])).first()
        if group is not None:
            ns_group.abort(409, 'Group already exists')

        created_group = create_group(payload['name'], payload['permissions'], current_user)
        return created_group, 200


@ns_group.route('/<int:id>')
@ns_group.doc(params={'id': 'Group ID.'})
@ns_group.resolve_object('group', lambda kwargs: Group.query.get_or_error(kwargs.pop('id')))
class GetGroup(Resource):
    @ns_group.doc(security='access_token')
    @ns_group.response(200, 'Success', group_model)
    @ns_group.response(401, 'Incorrect credentials')
    @ns_group.response(404, 'Group doesn\'t exist')
    @api.marshal_with(group_model)
    def get(self, group):
        """
                Returns group info.
        """
        return group, 200
