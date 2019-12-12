from sqlalchemy import func
from app.api import dgvost_api
from app.models import User, Group
from app.utils.create import new_group
from flask_restplus import Resource, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.utils.models import new_group_model, group_model

ns_group = Namespace('Group', description='Used to carry out operations related with groups.', path='/group')


@ns_group.route('/list')
class get_all_groups(Resource):
    @jwt_required
    @ns_group.doc(security='access_token')
    @ns_group.response(200, 'Success', [group_model])
    @ns_group.response(404, 'No groups exist')
    def get(self):
        """
                Returns all groups.
        """
        all_groups = [{'id': m.id, 'name': m.name, 'permissions': m.permissions} for m in Group.query.all()]
        if not all_groups:
            ns_group.abort(404, 'No groups exist')
        return all_groups, 200


@ns_group.route('/get/<int:id>')
class get_group(Resource):
    @jwt_required
    @ns_group.doc(security='access_token')
    @ns_group.response(200, 'Success', [group_model])
    @ns_group.response(401, 'Group doesn\'t exist')
    def get(self, id):
        """
                Returns group info.
        """
        group = Group.query.filter_by(id=id).first()
        if not group:
            ns_group.abort(401, 'Group doesn\'t exist')
        return {'id': group.id, 'name': group.name, 'permissions': group.permissions}, 200


@ns_group.route('/create')
class create_new_group(Resource):
    @jwt_required
    @ns_group.expect(new_group_model, validate=True)
    @ns_group.doc(security='access_token')
    @ns_group.response(200, 'Success', group_model)
    @ns_group.response(401, 'Incorrect credentials')
    @ns_group.response(403, 'Missing Supervisor permission')
    def post(self):
        """
                Creates a new group, requires the Supervisor permission. Supplying a list of permissions is optional.
        """
        payload = dgvost_api.payload
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        if not current_user.group.has_permission('Supervisor'):
            ns_group.abort(403, 'Missing Supervisor permission')

        group = Group.query.filter(func.lower(Group.name) == func.lower(payload['name'])).first()
        if group is not None:
            ns_group.abort(409, 'Group already exists')

        created_group = new_group(payload['name'], payload['permissions'], current_user)
        return {'group_id': created_group.id, 'name': created_group.name, 'permissions': created_group.permissions}, 200