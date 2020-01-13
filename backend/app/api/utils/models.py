from app.api import api
from flask_restx import fields

login_model = api.model('Login',
                               {'email': fields.String(required=True), 'password': fields.String(required=True)})

tokens_model = api.model('Token', {'access_token': fields.String(required=True),
                                          'refresh_token': fields.String(required=True)})

create_user_modal = api.model('Create User',
                                  {'firstname': fields.String(required=True), 'surname': fields.String(required=True),
                                   'email': fields.String(required=True), 'group_id': fields.Integer(
                                      description='Optional ID of the group for the user to be added to.')})

new_group_model = api.model('Create Group',
                                   {'name': fields.String(required=True), 'permissions': fields.List(fields.String)})


new_deployment_model = api.model('Create Deployment',  ##TODO Add areas
                                        {'name': fields.String(required=True), 'description': fields.String(),
                                         'group_ids': fields.List(fields.Integer,
                                                                  description='Leave blank for everyone to have access.'),
                                         'user_ids': fields.List(fields.Integer,
                                                                 description='Leave blank for everyone to have access.')})


new_incident_model = api.model('Create Incident',
                                      {'name': fields.String(required=True),
                                       'description': fields.String(required=True),
                                       'incident_type': fields.String(required=True),
                                       'location': fields.String(required=True),
                                       'longitude': fields.Float(required=True),
                                       'latitude': fields.Float(required=True), 'reported_via': fields.String(),
                                       'reference': fields.String()})  ##TODO Convert to GEOJson

point_geometry_model = api.model('Point Geometry', {
    'type': fields.String(default="Point"),
    'coordinates': fields.List(fields.Integer, attribute=lambda x: x.get_coordinates(), description='Longitude and latitude, in that order. Can return null too.', type="Array")
})

point_properties_model = api.model('Point Properties', {
    'address': fields.String(attribute='location')
})

point_feature_model = api.model('Point Feature', {
    'type': fields.String(default="Feature"),
    'geometry': fields.Nested(point_geometry_model, attribute=lambda x: x),
    'properties': fields.Nested(point_properties_model, attribute=lambda x: x)
})

group_model = api.model('Group', {'id': fields.Integer(), 'name': fields.String(), 'permissions': fields.List(fields.String, attribute=lambda x: x.get_permissions())})

user_model = api.model('User', {'id': fields.Integer(), 'firstname': fields.String(), 'surname': fields.String(), 'group': fields.Nested(group_model)})


deployment_model = api.model('Deployment',
                                    {'id': fields.Integer(), 'name': fields.String(), 'description': fields.String(),
                                     'open': fields.Boolean(attribute='open_status'),
                                     'created_at': fields.Float(attribute=lambda x: x.created_at.timestamp(), description='UTC Timestamp.'),
                                     'groups': fields.List(fields.Nested(group_model)), 'users': fields.List(fields.Nested(user_model)),
                                     'areas': fields.List(fields.String, description='List of LAD13CDO area codes.')})


incident_model = api.model('Incident',
                                  {'id': fields.Integer(), 'name': fields.String(), 'description': fields.String(),
                                   'type': fields.String(attribute='incident_type'),
                                   'open': fields.Boolean(attribute='open_status'), 'public': fields.Boolean(),
                                   'priority': fields.String(), 'location': fields.Nested(point_feature_model, attribute=lambda x: x, description='GeoJSON Point of the location.'),
                                   'created_at': fields.Float(attribute=lambda x: x.created_at.timestamp(), description='UTC Timestamp.')})

