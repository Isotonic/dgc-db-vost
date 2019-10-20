from app.api import c5_api
from flask_restplus import fields

login_model = c5_api.model('Login',
                           {'username': fields.String(required=True), 'password': fields.String(required=True)})

tokens_model = c5_api.model('Token', {'access_token': fields.String(required=True),
                                      'refresh_token': fields.String(required=True)})

new_user_model = c5_api.model('New User',
                              {'username': fields.String(required=True), 'email': fields.String(required=True),
                               'group': fields.String(
                                   description="Optional name of the group for the user to be added to.")})

return_user = c5_api.model('Return User',
                           {'user_id': fields.Integer(), "username": fields.String(), "group": fields.String()})

all_users_model = c5_api.model('Return All Users',
                               {"user_id": fields.Integer(), "username": fields.String(), "group": fields.String()})

new_group_model = c5_api.model('New Group',
                               {'name': fields.String(required=True), 'permissions': fields.List(fields.String)})

return_group = c5_api.model('Return Group', {'group_id': fields.Integer(), 'permission': fields.Integer()})

all_groups_model = c5_api.model('Return All Group', {"group_id": fields.Integer(), "name": fields.String(),
                                                     "permissions": fields.Integer()})
