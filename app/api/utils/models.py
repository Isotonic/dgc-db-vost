from app.api import dgvost_api
from flask_restplus import fields

login_model = dgvost_api.model('Login',
                               {'email': fields.String(required=True), 'password': fields.String(required=True)})

tokens_model = dgvost_api.model('Token', {'access_token': fields.String(required=True),
                                          'refresh_token': fields.String(required=True)})

new_user_model = dgvost_api.model('New User',
                                  {'firstname': fields.String(required=True), 'surname': fields.String(required=True),
                                   'email': fields.String(required=True), 'group_id': fields.Integer(
                                      description='Optional ID of the group for the user to be added to.')})

user_model = dgvost_api.model('User',
                              {'user_id': fields.Integer(), 'firstname': fields.String(), 'surname': fields.String(),
                               'avatar_url': fields.String, 'group_id': fields.Integer()})

new_group_model = dgvost_api.model('New Group',
                                   {'name': fields.String(required=True), 'permissions': fields.List(fields.String)})

group_model = dgvost_api.model('Group',
                               {'group_id': fields.Integer(), 'name': fields.String(), 'permission': fields.Integer()})

new_deployment_model = dgvost_api.model('New Deployment',  ##TODO Add areas
                                        {'name': fields.String(required=True), 'description': fields.String(),
                                         'group_ids': fields.List(fields.Integer,
                                                                  description='Leave blank for everyone to have access.'),
                                         'user_ids': fields.List(fields.Integer,
                                                                 description='Leave blank for everyone to have access.')})

deployment_model = dgvost_api.model('Deployment',
                                    {'id': fields.Integer(), 'name': fields.String(), 'description': fields.String(),
                                     'open': fields.Boolean(),
                                     'created_at': fields.Float(description='UTC Timestamp.'),
                                     'group_ids': fields.List(fields.Integer), 'user_ids': fields.List(fields.Integer,
                                                                                                       description='List of LAD13CDO area codes.'),
                                     'areas': fields.List(fields.Integer)})

new_incident_model = dgvost_api.model('New Incident',
                                      {'name': fields.String(required=True),
                                       'description': fields.String(required=True),
                                       'location': fields.String(required=True), 'reported_via': fields.String(),
                                       'reference': fields.String()})  ##TODO Convert to GEOJson

incident_model = dgvost_api.model('Incident',
                                  {'id': fields.Integer(), 'name': fields.String(), 'description': fields.String(),
                                   'location': fields.String(), 'open': fields.Boolean(), 'public': fields.Boolean(),
                                   'flagged': fields.Boolean(), 'type': fields.Integer(), 'priority': fields.Integer(),
                                   'longitude': fields.Float(), 'latitude': fields.Float(),
                                   'created_at': fields.Float(description='UTC Timestamp.')})
