from app.api import api
from flask_restx import fields

id_model = api.model('ID', {'id': fields.Integer(description='ID.')})

login_model = api.model('Login',
                       {'email': fields.String(description='Email address for account.', required=True), 'password': fields.String(description='Password for account.', required=True)})

tokens_model = api.model('Token',
                         {'access_token': fields.String(description='Access Token.', required=True),
                         'refresh_token': fields.String(description='Refresh Token.', required=True)})

create_user_modal = api.model('New User',
                          {'email': fields.String(description='Email address of new user.', required=True),
                           'group': fields.Integer(description='Optional ID of the group for the user to be added to, can be omitted.')})

new_group_model = api.model('New Group',
                           {'name': fields.String(description='Name of the group', required=True),
                            'supervisor': fields.Boolean(description='Admin access with full control, inherits all other permissions.', required=True),
                            'create_deployment': fields.Boolean(description='Create new deployments and edit existing ones.', required=True),
                            'view_all_incidents': fields.Boolean(description='View incidents even if not assigned.', required=True),
                            'change_priority': fields.Boolean(description='Change an incident\'s priority.', required=True),
                            'change_status': fields.Boolean(description='Change an incident\'s open status.', required=True),
                            'change_allocation': fields.Boolean(description='Change an incident\'s allocation.', required=True),
                            'mark_as_public': fields.Boolean(description='Change if an incident or incident comment if viewable by the public or not.', required=True)})


new_deployment_model = api.model('New Deployment',
                                {'name': fields.String(description='Name of the deployment.', required=True),
                                 'description': fields.String(description='Description of the deployment.'),
                                 'groups': fields.List(fields.Integer, description='Group IDs to whitelist, leave blank for everyone to have access.'),
                                 'users': fields.List(fields.Integer, description='User IDs to whitelist, leave blank for everyone to have access.')})

edit_deployment_model = api.model('Edit Deployment',
                                {'name': fields.String(description='Name of the deployment', required=True),
                                 'description': fields.String(description='Description of the deployment.'),
                                 'open': fields.Boolean(description='Open status of the deployment.', required=True),
                                 'groups': fields.List(fields.Integer, description='Group IDs to whitelist, leave blank for everyone to have access.'),
                                 'users': fields.List(fields.Integer, description='User IDs to whitelist, leave blank for everyone to have access.')})

new_comment_model = api.model('New Comment',
                              {'text': fields.String(required=True, description='Comment text.'),
                               'public': fields.Boolean(description='If the comment will be viewable by the public once the incident is marked public. Field will be ignored if you don\'t have the mark as public permission and defaulted to False. Optionally omit this field.')})

new_task_model = api.model('New Task',
                           {'name': fields.String(required=True, description='Task name.'),
                            'description': fields.String(description='Optional description of the task.'),
                            'assignedTo': fields.List(fields.Integer, description='Optional list of user IDs assigned to the task.')})

new_incident_model = api.model('Create Incident',
                              {'name': fields.String(description='Name of the incident.', required=True),
                               'description': fields.String(description='Description of the incident.', required=True),
                               'type': fields.String(description='Type of incident.', required=True),
                               'address': fields.String(description='Address of the incident.', required=True),
                               'longitude': fields.Float(description='Longitude of the incident.', required=True),
                               'latitude': fields.Float(description='Latitude of the incident.', required=True),
                               'reportedVia': fields.String(description='Incident reported via.'),
                               'reference': fields.String(description='Incident reference.')})

edit_incident_model = api.model('Edit Incident',
                              {'name': fields.String(description='Name of incident', required=True),
                               'description': fields.String(description='Description of incident.'),
                               'type': fields.String(description='Type of incident.', required=True),
                               'reportedVia': fields.String(description='Incident reported via.'),
                               'linkedIncidents': fields.List(fields.Integer, description='Incidents linked to this incident.'),
                               'reference': fields.String(description='Incident reference.')})


point_geometry_model = api.model('Point Geometry', {
                                'type': fields.String(default='Point'),
                                'coordinates': fields.List(fields.Float, attribute=lambda x: x.get_coordinates(), description='Longitude and latitude.', type='Array')})

point_properties_model = api.model('Point Properties', {'address': fields.String(attribute='location', description='Address of the incident.')})

point_feature_model = api.model('Point Feature', {
                                'type': fields.String(default='Feature'),
                                'geometry': fields.Nested(point_geometry_model, attribute=lambda x: x),
                                'properties': fields.Nested(point_properties_model, attribute=lambda x: x)})

user_model_without_group = api.model('User Without Group',
                        {'id': fields.Integer(description='ID of the user.'),
                         'firstname': fields.String(description='Firstname of the user.'),
                         'surname': fields.String(description='Surname of the user.'),
                         'avatarUrl': fields.String(attribute=lambda x: x.get_avatar() if x else '', description='URL for the user\'s avatar.')})

group_model_without_users = api.model('Group Without Users',
                        {'id': fields.Integer(description='ID of the group.'),
                         'name': fields.String(description='Name of the group.'),
                         'permissions': fields.List(fields.String, attribute=lambda x: x.get_permissions() if x else None, description='Group\'s permissions.')})

group_model = api.model('Group',
                        {'id': fields.Integer(description='ID of the group.'),
                         'name': fields.String(description='Name of the group.'),
                         'users': fields.Nested(user_model_without_group, description='Users in the group.'),
                         'permissions': fields.List(fields.String, attribute=lambda x: x.get_permissions() if x else None, description='Group\'s permissions.')})


user_model = api.model('User Slimmed',
                        {'id': fields.Integer(description='ID of the user.'),
                         'firstname': fields.String(description='Firstname of the user.'),
                         'surname': fields.String(description='Surname of the user.'),
                         'avatarUrl': fields.String(attribute=lambda x: x.get_avatar(), description='URL for the user\'s avatar.'),
                         'group': fields.Nested(group_model_without_users, allow_null=True, description='Group the user belongs to, can be empty too.')})

user_admin_panel_model = api.model('User Detailed',
                        {'id': fields.Integer(description='ID of the user.'),
                         'firstname': fields.String(description='Firstname of the user.'),
                         'surname': fields.String(description='Surname of the user.'),
                         'email': fields.String(description='Email of the user.'),
                         'createdAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the user\'s creation.'),
                         'status': fields.String(description='Status of the user. -1 = Disabled account, 0 = Sent email, 1 = Active account.'),
                         'avatarUrl': fields.String(attribute=lambda x: x.get_avatar(), description='URL for the user\'s avatar.'),
                         'group': fields.Nested(group_model_without_users, allow_null=True, description='Group the user belongs to, can be empty too.')})

notification_model = api.model('Notification',
                        {'id': fields.Integer(description='ID of the notification.'),
                         'deploymentId': fields.Integer(attribute='deployment_id', description='ID of the deployment related to the notification.'),
                         'deploymentName': fields.String(attribute=lambda x: x.deployment.name, description='Name of the deployment related to the notification.'),
                         'incidentId': fields.Integer(attribute='incident_id', description='ID of the incident related to the notification.'),
                         'incidentName': fields.String(attribute=lambda x: x.incident.name, description='Name of the incident related to the notification.'),
                         'taskId': fields.Integer(attribute='task_id', description='ID of the task related to the notification, can be null if no task.'),
                         'taskName': fields.String(attribute=lambda x: x.task.name if x.task else None, description='Name of the task related to the notification, can be null if no task.'),
                         'subtaskId': fields.Integer(attribute='subtask_id', description='ID of the subtask related to the notification, can be null if no subtask.'),
                         'subtaskName': fields.String(attribute=lambda x: x.subtask.name if x.subtask else None, description='Name of the subtask related to the notification, can be null if no subtask.'),
                         'type': fields.String(attribute='action_type', description='Type of notification'),
                         'triggeredBy': fields.Nested(user_model, attribute='triggered_by', description='User who triggered the notification.'),
                         'reason': fields.String(description='Reason as to why the user triggered the notification, can be null'),
                         'occurredAt': fields.Integer(attribute=lambda x: int(x.triggered_at.timestamp()), description='UTC timestamp of when the notification occurred.')})

user_full_details_model = api.model('User',
                        {'id': fields.Integer(description='ID of the user.'),
                         'firstname': fields.String(description='Firstname of the user.'),
                         'surname': fields.String(description='Surname of the user.'),
                         'email': fields.String(description='Email of the user.'),
                         'createdAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the user\'s creation.'),
                         'status': fields.String(description='Status of the user. -1 = Disabled account, 0 = Sent email, 1 = Active account and 2 = Superuser.'),
                         'avatarUrl': fields.String(attribute=lambda x: x.get_avatar(), description='URL for the user\'s avatar.'),
                         'group': fields.Nested(group_model_without_users, allow_null=True, description='Group the user belongs to, can be empty too.'),
                         'notifications': fields.Nested(notification_model, description='Notifications the user has.')})

deployment_model = api.model('Deployment',
                            {'id': fields.Integer(description='ID of the deployment.'),
                             'name': fields.String(description='Name of the deployment.'),
                             'description': fields.String(description='Description of the deployment.'),
                             'open': fields.Boolean(attribute='open_status', description='Open status of the deployment.'),
                             'createdAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the deployment\'s creation.'),
                             'closedAt': fields.Integer(attribute=lambda x: int(x.closed_at.timestamp()) if x.closed_at else None, description='UTC timestamp of the deployment\'s closure, can be null.'),
                             'groups': fields.List(fields.Nested(group_model), description='Whitelisted groups that are able to access this deployment, if both users and groups are empty then all users and groups have access to it.'),
                             'users': fields.List(fields.Nested(user_model_without_group), description='Whitelisted users that are able to access this deployment, if both users and groups are empty then all users and groups have access to it.')})

activity_model = api.model('Activity',
                           {'id': fields.Integer(description='ID of the activity.'),
                            'user': fields.Nested(user_model, description='User who carried out the action.'),
                            'comment': fields.String(description='Comment text, can be null.'),
                            'commentId': fields.String(attribute='comment_id', description='Comment id, can be null.'),
                            'task': fields.String(description='Task name, can be null.'),
                            'taskId': fields.String(attribute='task_id', description='Task id, can be null.'),
                            'subtask': fields.String(description='Subtask name, can be null.'),
                            'subtaskId': fields.String(attribute='subtask_id', description='Subtask id, can be null.'),
                            'targetUsers': fields.Nested(user_model, attribute='target_users', description='Affected users, can be null.'),
                            'extra': fields.String(description='Extra text, can be null.'),
                            'type': fields.String(attribute=lambda x: x.get_action_type(), description='Type of action taken.'),
                            'occurredAt': fields.Integer(attribute=lambda x: int(x.occurred_at.timestamp()), description='UTC timestamp of when the activity occurred.')})

task_activity_model = api.model('Task Activity',
                           {'id': fields.Integer(description='ID of the activity.'),
                            'task': fields.String(attribute=lambda x: x.task.name, description='Task name.'),
                            'user': fields.Nested(user_model, description='User who carried out the action.'),
                            'subtask': fields.String(attribute=lambda x: x.subtask.name if x.subtask else None, description='Subtask name, can be null.'),
                            'subtaskId': fields.String(attribute='subtask_id', description='Subtask id, can be null.'),
                            'targetUsers': fields.Nested(user_model, attribute='target_users', description='Affected users, can be null.'),
                            'extra': fields.String(description='Extra text, can be null.'),
                            'type': fields.String(attribute=lambda x: x.get_action_type(), description='Type of action taken.'),
                            'occurredAt': fields.Integer(attribute=lambda x: int(x.occurred_at.timestamp()), description='UTC timestamp of when the activity occurred.')})

comment_model = api.model('Comment',
                            {'id': fields.Integer(description='ID of the comment.'),
                             'user': fields.Nested(user_model_without_group, description='The user that sent the comment.'),
                             'text': fields.String(description='Comment text, can be a stringified ProseMirror JSON object.'),
                             'public': fields.Boolean(required=True, description='If the comment will be viewable by the public once the incident is marked public.'),
                             'sentAt': fields.Integer(attribute=lambda x: int(x.sent_at.timestamp()), description='UTC timestamp of when the update was sent.'),
                             'editedAt': fields.Integer(attribute=lambda x: int(x.edited_at.timestamp()) if x.edited_at else None, description='UTC timestamp of when the update was last edited at, can be null.')})

public_comment_model = api.model('Public Comment',
                            {'id': fields.Integer(description='ID of the comment.'),
                             'text': fields.String(description='Comment text, can be a stringified ProseMirror JSON object.'),
                             'sentAt': fields.Integer(attribute=lambda x: int(x.sent_at.timestamp()), description='UTC timestamp of when the update was sent.'),
                             'editedAt': fields.Integer(attribute=lambda x: int(x.edited_at.timestamp()) if x.edited_at else None, description='UTC timestamp of when the update was last edited at, can be null.')})

subtask_model = api.model('Subtask',
                            {'id': fields.Integer(description='Subtask ID.'),
                             'name': fields.String(description='Subtask name.'),
                             'completed': fields.Boolean(description='Subtask completion status.'),
                             'createdAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the subtask\'s creation.'),
                             'completedAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the subtask\'s completion, will be null if it isn\'t completed.'),
                             'assignedTo': fields.List(fields.Nested(user_model_without_group), description='Users assigned to, can be empty.', attribute='assigned_to')})

task_comment_model = api.model('Task Comment',
                            {'id': fields.Integer(description='ID of the comment.'),
                             'user': fields.Nested(user_model_without_group, description='The user that sent the comment.'),
                             'text': fields.String(description='Comment text, can be a stringified ProseMirror JSON object.'),
                             'sentAt': fields.Integer(attribute=lambda x: int(x.sent_at.timestamp()), description='UTC timestamp of when the update was sent.'),
                             'editedAt': fields.Integer(attribute=lambda x: int(x.edited_at.timestamp()) if x.edited_at else None, description='UTC timestamp of when the update was last edited at, can be null.')})

task_model = api.model('Task',
                        {'id': fields.Integer(description='ID of the task.'),
                         'name': fields.String(description='Name of the task.'),
                         'description': fields.String(description='Description of the task.'),
                         'tags': fields.List(fields.String, attribute=lambda x: x.tags if x.tags else [], description='Tags given to a task, can be empty.'),
                         'completed': fields.Boolean(description='If the task is marked as complete or not.'),
                         'createdAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the task\'s creation.'),
                         'completedAt': fields.Integer(attribute=lambda x: int(x.completed_at.timestamp()) if x.completed_at else None, description='UTC timestamp of the task\'s completion, will be null if it isn\'t completed.'),
                         'assignedTo': fields.List(fields.Nested(user_model_without_group), attribute='assigned_to', description='User\'s the task is assigned to, can be empty.'),
                         'subtasks': fields.List(fields.Nested(subtask_model), description='Tasks within the task, can be empty.'),
                         'comments': fields.List(fields.Nested(task_comment_model), description='Comments in the task, can be empty.'),
                         'activity': fields.List(fields.Nested(task_activity_model), attribute='task_actions', description='Actions the occured in the task.')})


task_model_with_incident = api.model('Task With Incident',
                        {'id': fields.Integer(description='ID of the task.'),
                         'incidentId': fields.Integer(attribute=lambda x: x.incident_id, description='ID of the incident. it belongs to.'),
                         'deploymentId': fields.Integer(attribute=lambda x: x.incident.deployment_id, description='ID of the deployment it belongs to.'),
                         'name': fields.String(description='Name of the task.'),
                         'description': fields.String(description='Description of the task.'),
                         'tags': fields.List(fields.String, attribute=lambda x: x.tags if x.tags else [], description='Tags given to a task, can be empty.'),
                         'completed': fields.Boolean(description='If the task is marked as complete or not.'),
                         'createdAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the task\'s creation.'),
                         'completedAt': fields.Integer(attribute=lambda x: int(x.completed_at.timestamp()) if x.completed_at else None, description='UTC timestamp of the task\'s completion, will be null if it isn\'t completed.'),
                         'assignedTo': fields.List(fields.Nested(user_model_without_group), attribute='assigned_to', description='User\'s the task is assigned to, can be empty.'),
                         'subtasks': fields.List(fields.Nested(subtask_model), description='Tasks within the task, can be empty.'),
                         'comments': fields.List(fields.Nested(task_comment_model), description='Comments in the task, can be empty.'),
                         'activity': fields.List(fields.Nested(task_activity_model), attribute='task_actions', description='Actions the occured in the task.')})


incident_model_name = api.model('Incident Name',
                            {'id': fields.Integer(description='ID of the incident.'),
                             'name': fields.String(description='Name of the incident.')})


incident_model = api.model('Incident',
                            {'id': fields.Integer(description='ID of the incident.'),
                             'name': fields.String(description='Name of the incident.'),
                             'publicName': fields.String(attribute='public_name', description='Public name of the incident, can be null.'),
                             'description': fields.String(description='Description of the incident.'),
                             'publicDescription': fields.String(attribute='public_description', description='Description of the incident that is viewable by the public when incident is marked public, can be null.'),
                             'type': fields.String(attribute='incident_type', description='Type of incident.'),
                             'open': fields.Boolean(attribute='open_status', description='Open status of the incident.'),
                             'public': fields.Boolean(description='If the incident is viewable by the public.'),
                             'priority': fields.String(description='Priority level of the incident.'),
                             'icon': fields.String(attribute=lambda x: x.get_icon(), description='FontAwesome Icon.'),
                             'location': fields.Nested(point_feature_model, attribute=lambda x: x, description='GeoJSON Point of the location.'),
                             'reportedVia': fields.String(attribute='reported_via', description='Method of reporting.'),
                             'loggedBy': fields.Nested(user_model, attribute='created_by_user', description='The user the incident was created by.'),
                             'referenceNo': fields.String(attribute='reference', description='Reference number, can be null too.'),
                             'pinned': fields.Boolean(description='If the user has this pinned or not.'),
                             'linkedIncidents': fields.List(fields.Nested(incident_model_name), attribute='linked', description='Incidents linked to this one.'),
                             'createdAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the incident\'s creation.'),
                             'closedAt': fields.Integer(attribute=lambda x: int(x.closed_at.timestamp()) if x.closed_at else None, description='UTC timestamp of the incident\'s closure, can be null.'),
                             'lastUpdatedAt': fields.Integer(attribute=lambda x: int(x.last_updated.timestamp()), description='UTC timestamp of the incident\'s last update.'),
                             'assignedTo': fields.List(fields.Nested(user_model_without_group), attribute='assigned_to', description='User\'s the incident is assigned to, can be empty.'),
                             'tasks': fields.List(fields.Nested(task_model), description='Tasks in the incident, can be empty.'),
                             'comments': fields.List(fields.Nested(comment_model), description='Comments in the incidents, can be empty.'),
                             'activity': fields.List(fields.Nested(activity_model), attribute='actions', description='Actions the occured in the incident.')})

public_incident_model = api.model('Public Incident',
                            {'id': fields.Integer(description='ID of the incident.'),
                             'deployment': fields.String(description='Deployment the incident belongs to'),
                             'name': fields.String(attribute=lambda x: x.public_name if x.public_name else x.name, description='Name of the incident.'),
                             'description': fields.String(attribute=lambda x: x.public_description if x.public_description else x.description, description='Description of the incident, can be null.'),
                             'type': fields.String(attribute='incident_type', description='Type of incident.'),
                             'open': fields.Boolean(attribute='open_status', description='Open status of the incident.'),
                             'icon': fields.String(attribute=lambda x: x.get_icon(), description='FontAwesome Icon.'),
                             'location': fields.Nested(point_feature_model, attribute=lambda x: x, description='GeoJSON Point of the location.'),
                             'createdAt': fields.Integer(attribute=lambda x: int(x.created_at.timestamp()), description='UTC timestamp of the incident\'s creation.'),
                             'lastUpdatedAt': fields.Integer(attribute=lambda x: x.get_last_public_updated_at(), description='UTC timestamp of the incident\'s last update.'),
                             'comments': fields.List(fields.Nested(public_comment_model), attribute=lambda x: x.public_comments())})

pinned_model = api.model('Pinned', {'pinned': fields.Boolean(description='Pinned status.', required=True)})

status_model = api.model('Status', {'open': fields.Boolean(attribute='open_status', description='Open status.', required=True)})

completion_model = api.model('Completion', {'completed': fields.Boolean(description='Completed status.', required=True)})

name_model = api.model('Name', {'name': fields.String(description='Task name.', required=True)})

priority_model = api.model('Priority', {'priority': fields.String(description='Priority level of the incident.', required=True)})

public_model = api.model('Public', {'public': fields.Boolean(description='If an incident is viewable by the public or not.', required=True),
                                    'name': fields.String(description='Optional name of the incident, can be left null to default to the existing incident name.'),
                                    'description': fields.String(description='Optional description of the incident, can be left null to default to the existing incident description.')})

text_model = api.model('Text', {'text': fields.String(description='Comment text, can be a stringified ProseMirror JSON object.', required=True)})

comment_edited_model = api.model('Commented Edited', {'text': fields.String(description='Comment text, can be a stringified ProseMirror JSON object.', required=True),
                                                      'editedAt': fields.Integer(attribute=lambda x: int(x.edited_at.timestamp()), description='UTC timestamp of when the update was last edited at.')})

new_subtask_model = api.model('New Subtask',
                            {'name': fields.String(description='Name of subtask.', required=True),
                             'assignedTo': fields.List(fields.Integer(), description='Optional IDs of the assigned users.')})

tags_model = api.model('Tags', {'tags': fields.List(fields.String, attribute=lambda x: x.tags if x.tags else [], required=True, description='Tags given to a task, can be an empty.')})

email_model = api.model('Email', {'email': fields.String(description='Email address.', required=True)})

password_reset_model = api.model('Password Reset', {'password': fields.String(description='Password, must be at least 8 characters, contain a lowercase and uppercase letter and contain a number.', required=True)})


registration_model = api.model('Registration', {'firstname': fields.String(description='Firstname of the user.', required=True),
                                                'surname': fields.String(description='Surname of the user.', required=True),
                                                'password': fields.String(description='Password, must be at least 8 characters, contain a lowercase and uppercase letter and contain a number.', required=True)})


edit_user_details_model = api.model('Edit User Details', {'firstname': fields.String(description='Firstname of the user.', required=True),
                                                          'surname': fields.String(description='Surname of the user.', required=True),
                                                          'email': fields.String(description='Email of the user.', required=True),
                                                          'currentPassword': fields.String(description='Password of the user.', required=True),
                                                          'newPassword': fields.String(description='Optional new password, must be at least 8 characters, contain a lowercase and uppercase letter and contain a number.')})


updated_user_details_model = api.model('Updated User Details', {'firstname': fields.String(description='Firstname of the user.', required=True),
                                                                'surname': fields.String(description='Surname of the user.', required=True),
                                                                'email': fields.String(description='Email of the user.', required=True),
                                                                'access_token': fields.String(description='If the password was changed then a new access token will also be sent.'),
                                                                'refresh_token': fields.String(description='If the password was changed then a new refresh token will also be sent.')})


change_location_model = api.model('Change location',
                                {'address': fields.String(required=True),
                                 'longitude': fields.Float(required=True),
                                 'latitude': fields.Float(required=True)})


action_required_model = api.model('Actions Required',
                                 {'id': fields.Integer(description='ID of the requested action.'),
                                  'incident': fields.Nested(incident_model_name, attribute='incident'),
                                  'requestedBy': fields.Nested(user_model_without_group, attribute='requested_by'),
                                  'type': fields.String(attribute='action_type'),
                                  'reason': fields.String(),
                                  'requestedAt': fields.Integer(attribute=lambda x: int(x.requested_at.timestamp()))})

mark_dealt_with_model = api.model('Mark Dealt With', {'carryOutAction': fields.Boolean(description='Optional carrying out of action if it\'s changing the incident\'s status.')})

flag_user_model = api.model('Flag To User', {'id': fields.Integer(description='ID of the user.', required=True), 'reason': fields.String(description='Reason for flagging.', required=True)})

flag_supervisor_model = api.model('Flag Supervisor', {'reason': fields.String(description='Reason for flagging.', required=True)})

status_change_reason_model = api.model('Reason', {'reason': fields.String(description='Optional reason for requesting status change')})

public_deployment_model = api.model('Public Deployment',
                            {'id': fields.Integer(description='ID of the deployment.'),
                             'name': fields.String(description='Name of the deployment.'),
                             'description': fields.String(description='Description of the deployment.')})

user_status_model = api.model('User Status', {'status': fields.Integer(description='Status of the user. -1 = Disabled account, 0 = Sent email, 1 = Active account and 2 = Superuser.', required=True)})

avatar_model = api.model('Avatar',
                        {'avatarUrl': fields.String(attribute=lambda x: x.get_avatar() if x else '', description='URL for the user\'s avatar.')})
