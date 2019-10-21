from app.api import c5_api
from flask_restplus import fields

login_model = c5_api.model('Login',
                           {'username': fields.String(required=True), 'password': fields.String(required=True)})

tokens_model = c5_api.model('Token', {'access_token': fields.String(required=True),
                                      'refresh_token': fields.String(required=True)})

new_user_model = c5_api.model('New User',
                              {'username': fields.String(required=True), 'email': fields.String(required=True),
                               'group_id': fields.Integer(
                                   description='Optional ID of the group for the user to be added to.')})

user_model = c5_api.model('User',
                          {'user_id': fields.Integer(), 'username': fields.String(), 'group_id': fields.Integer()})

new_group_model = c5_api.model('New Group',
                               {'name': fields.String(required=True), 'permissions': fields.List(fields.String)})

group_model = c5_api.model('Group',
                           {'group_id': fields.Integer(), 'name': fields.String(), 'permission': fields.Integer()})

new_deployment_model = c5_api.model('New Deployment',
                                    {'name': fields.String(required=True), 'description': fields.String(),
                                     'groups': fields.List(fields.Integer,
                                                           description='Leave blank for everyone to have access.'),
                                     'users': fields.List(fields.Integer,
                                                          description='Leave blank for everyone to have access.')})

deployment_model = c5_api.model('Deployment',
                                {'id': fields.Integer(), 'name': fields.String(), 'description': fields.String(),
                                 'open': fields.Boolean(), 'created_at': fields.DateTime(dt_format='iso8601'),
                                 'groups': fields.List(fields.Integer), 'users': fields.List(fields.Integer)})
new_incident_model = c5_api.model('New Incident',
                                  {'name': fields.String(required=True), 'description': fields.String(required=True),
                                   'location': fields.String(required=True)})

incident_model = c5_api.model('Incident',
                              {'id': fields.Integer(), 'name': fields.String(), 'description': fields.String(),
                               'location': fields.String(), 'open': fields.Boolean(), 'public': fields.Boolean(),
                               'flagged': fields.Boolean(), 'type': fields.Integer(), 'priority': fields.Integer(),
                               'xcoord': fields.Float(), 'ycoord': fields.Float(),
                               'created_at': fields.DateTime(dt_format='iso8601')})
