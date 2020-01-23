from app.api import api
from flask_restx import fields

id_model = api.model('ID', {'id': fields.Integer()})

login_model = api.model('Login',
                               {'email': fields.String(required=True), 'password': fields.String(required=True)})

tokens_model = api.model('Token', {'access_token': fields.String(required=True),
                                          'refresh_token': fields.String(required=True)})

create_user_modal = api.model('New User',
                                  {'firstname': fields.String(required=True), 'surname': fields.String(required=True),
                                   'email': fields.String(required=True), 'group_id': fields.Integer(
                                      description='Optional ID of the group for the user to be added to.')})

new_group_model = api.model('New Group',
                                   {'name': fields.String(required=True), 'permissions': fields.List(fields.String)})


new_deployment_model = api.model('New Deployment',  ##TODO Add areas
                                        {'name': fields.String(required=True), 'description': fields.String(),
                                         'group_ids': fields.List(fields.Integer,
                                                                  description='Leave blank for everyone to have access.'),
                                         'user_ids': fields.List(fields.Integer,
                                                                 description='Leave blank for everyone to have access.')})

new_comment_model = api.model('New Comment', {'text': fields.String(required=True, description='Comment text.')})

new_incident_model = api.model('Create Incident',
                                      {'name': fields.String(required=True),
                                       'description': fields.String(required=True),
                                       'incident_type': fields.String(required=True),
                                       'location': fields.String(required=True),
                                       'longitude': fields.Float(required=True),
                                       'latitude': fields.Float(required=True), 'reported_via': fields.String(),
                                       'reference': fields.String()})  ##TODO Convert to GEOJson

point_geometry_model = api.model('Point Geometry', {
    'type': fields.String(default='Point'),
    'coordinates': fields.List(fields.Integer, attribute=lambda x: x.get_coordinates(), description='Latitude and longitude.', type='Array')
})

point_properties_model = api.model('Point Properties', {
    'address': fields.String(attribute='location', description='Address of the incident.')
})

point_feature_model = api.model('Point Feature', {
    'type': fields.String(default='Feature'),
    'geometry': fields.Nested(point_geometry_model, attribute=lambda x: x),
    'properties': fields.Nested(point_properties_model, attribute=lambda x: x)
})

user_model_without_group = api.model('User Without Group',
                        {'id': fields.Integer(description='ID of the user.'),
                        'firstname': fields.String(description='Firstname of the user.'),
                        'surname': fields.String(description='Surname of the user.'),
                        'avatarUrl': fields.String(attribute=lambda x: x.get_avatar(), description='URL for the user\'s avatar.')})

group_model = api.model('Group',
                        {'id': fields.Integer(description='ID of the group.'),
                        'name': fields.String(description='Name of the group.'),
                        'users': fields.Nested(user_model_without_group, description='Users in the group.'),
                        'permissions': fields.List(fields.String, attribute=lambda x: x.get_permissions() if x else None, description='Group\'s permissions.')})

user_model = api.model('User',
                        {'id': fields.Integer(description='ID of the user.'),
                        'firstname': fields.String(description='Firstname of the user.'),
                        'surname': fields.String(description='Surname of the user.'),
                        'avatarUrl': fields.String(attribute=lambda x: x.get_avatar(), description='URL for the user\'s avatar.'),
                        'group': fields.Nested(group_model, skip_none=True, description='Group the user belongs to, can be empty too.')})


deployment_model = api.model('Deployment',
                            {'id': fields.Integer(description='ID of the deployment.'),
                            'name': fields.String(description='Name of the deployment.'),
                            'description': fields.String(description='Description of the deployment.'),
                            'open': fields.Boolean(attribute='open_status', description='Open status of the incident.'),
                            'createdAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the deployment\'s creation.'),
                            'groups': fields.List(fields.Nested(group_model), description='Whitelisted groups that are able to access this deployment, if both users and groups are empty then all users and groups have access to it.'),
                            'users': fields.List(fields.Nested(user_model), description='Whitelisted users that are able to access this deployment, if both users and groups are empty then all users and groups have access to it.'),
                            'areas': fields.List(fields.String, description='List of LAD13CDO area codes.')})

activity_model = api.model('Activity',
                           {'id': fields.Integer(),
                            'user': fields.Nested(user_model),
                            'text': fields.String(attribute=lambda x: str(x)),
                            'occurredAt': fields.Integer(attribute=lambda x: int(x.occurred_at.timestamp()))})

comment_model = api.model('Comment',
                            {'id': fields.Integer(description='ID of the comment.'),
                            'user': fields.Nested(user_model, description='The user that sent the comment.'),
                            'text': fields.String(description='Comment text, can be a stringified ProseMirror JSON object.'),
                            'sentAt': fields.Integer(attribute=lambda x: int(x.sent_at.timestamp()), description='UTC timestamp of when the update was sent.')})

subtask_model = api.model('Subtask',
                            {'id': fields.Integer(),
                            'name': fields.String(),
                            'completed': fields.Boolean(),
                            'createdAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the subtask\'s creation.'),
                            'completedAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the subtask\'s completion, will be null if it isn\'t completed.'),
                            'assignedTo': fields.List(fields.Nested(user_model), attribute='assigned_to')})

task_model = api.model('Task',
                        {'id': fields.Integer(),
                        'name': fields.String(),
                        'description': fields.String(),
                        'completed': fields.Boolean(),
                        'createdAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the task\'s creation.'),
                        'completedAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the task\'s completion, will be null if it isn\'t completed.'),
                        'assignedTo': fields.List(fields.Nested(user_model), attribute='assigned_to'),
                        'subtasks': fields.List(fields.Nested(subtask_model)),
                        'comments': fields.List(fields.Nested(comment_model)),
                        'logs': fields.List(fields.Nested(activity_model))}) ##TODO Change to actions

incident_model = api.model('Incident',
                            {'id': fields.Integer(description='ID of the incident.'),
                            'name': fields.String(description='Name of the incident.'),
                            'description': fields.String(description='Description of the incident.'),
                            'type': fields.String(attribute='incident_type', description='Type of incident.'),
                            'open': fields.Boolean(attribute='open_status', description='Open status of the incident.'),
                            'public': fields.Boolean(description='If the incident is viewable by the public.'),
                            'priority': fields.String(description='Priority level of the incident.'),
                            'icon': fields.String(attribute=lambda x: x.get_icon(), description='FontAwesome Icon.'),
                            'location': fields.Nested(point_feature_model, attribute=lambda x: x, description='GeoJSON Point of the location.'),
                            'reportedVia': fields.String(attribute='reported_via', description='Method of reporting.'),
                            'loggedBy': fields.Nested(user_model, attribute='created_by_user', description='The user the incident was created by.'),
                            'referenceNo': fields.String(attribute='reference', description='Reference number, can be null too.'),
                            #'pinned': fields.Boolean(attribute=lambda x: x, description='GeoJSON Point of the location.'),
                            'createdAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the incident\'s creation.'),
                            'lastUpdatedAt': fields.Integer(attribute=lambda x: int(x.last_updated.timestamp()), description='UTC timestamp of the incident\'s last update.'),
                            'assignedTo': fields.List(fields.Nested(user_model), attribute='assigned_to'),
                            'tasks': fields.List(fields.Nested(task_model)),
                            'comments': fields.List(fields.Nested(comment_model)),
                            'activity': fields.List(fields.Nested(activity_model), attribute='actions')})

status_model = api.model('Status', {'open': fields.Boolean(attribute='open_status', description='Open status.', required=True)})

completion_model = api.model('Completion', {'completed': fields.Boolean(description='Completed status.', required=True)})

priority_model = api.model('Priority', {'priority': fields.String(description='Priority level of the incident.', required=True)})

public_model = api.model('Public', {'public': fields.Boolean(description='If an incident is viewable by the public or not.', required=True)})

