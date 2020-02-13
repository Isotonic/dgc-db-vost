from ..api import api
from sqlalchemy import func
from ..models import User, Group
from .utils.resource import Resource
from ..utils.change import edit_group
from .utils.namespace import Namespace
from ..utils.create import create_group
from ..utils.delete import delete_group
from flask_jwt_extended import jwt_required, get_jwt_identity
from .utils.models import new_group_model, group_model

ns_group = Namespace('Group', description='Used to carry out actions related to groups.', path='/groups', decorators=[jwt_required])


@ns_group.route('')
class GroupsEndpoint(Resource):
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
    @ns_group.response(400, 'Name is empty')
    @ns_group.response(401, 'Incorrect credentials')
    @ns_group.response(403, 'Missing supervisor permission')
    @ns_group.response(403, 'Group already exists with this name')
    @api.marshal_with(group_model)
    def post(self):
        """
                Creates a new group, requires the supervisor permission.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        ns_group.has_permission(current_user, 'supervisor')

        group = Group.query.filter(func.lower(Group.name) == func.lower(payload['name'])).first()
        if group is not None:
            ns_group.abort(409, 'Group already exists with this name')

        permissions = []

        for x in Group.permission_values.keys():
            try:
                if payload[x]:
                    permissions.append(x)
            except KeyError:
                pass

        created_group = create_group(payload['name'], permissions, current_user)
        if created_group is False:
            ns_group.abort(400, 'Name is empty')
        return created_group, 200


@ns_group.route('/<int:id>')
@ns_group.doc(params={'id': 'Group ID.'})
@ns_group.resolve_object('group', lambda kwargs: Group.query.get_or_error(kwargs.pop('id')))
class GroupEndpoint(Resource):
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


    @ns_group.expect(new_group_model, validate=True)
    @ns_group.doc(security='access_token')
    @ns_group.response(200, 'Success', group_model)
    @ns_group.response(400, 'Name is empty')
    @ns_group.response(400, 'Nothing has been changed')
    @ns_group.response(401, 'Incorrect credentials')
    @ns_group.response(403, 'Missing supervisor permission')
    @ns_group.response(409, 'Group already exists with this name')
    @api.marshal_with(group_model)
    def put(self, group):
        """
                Edit's a group.
        """
        payload = api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        ns_group.has_permission(current_user, 'supervisor')

        if payload['name'] == '':
            ns_group.abort(400, 'Name is empty')

        other_group = Group.query.filter(func.lower(Group.name) == func.lower(payload['name']), Group.id != group.id).first()
        if other_group is not None:
            ns_group.abort(409, 'Group already exists with this name')

        permissions = []

        for x in Group.permission_values.keys():
            try:
                if payload[x]:
                    permissions.append(x)
            except KeyError:
                pass
        print(permissions)

        if edit_group(group, payload['name'], permissions, current_user) is False:
            ns_group.abort(400, 'Nothing has been changed')
        return group, 200


    @ns_group.doc(security='access_token')
    @ns_group.response(200, 'Success')
    @ns_group.response(400, 'Name is empty')
    @ns_group.response(401, 'Incorrect credentials')
    @ns_group.response(403, 'Missing supervisor permission')
    def delete(self, group):
        """
                Deletes a group.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        ns_group.has_permission(current_user, 'supervisor')
        delete_group(group, current_user)
        return 'Success', 200
