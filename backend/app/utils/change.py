import re
from app import db
from . import supervisor
from datetime import datetime
from flask_restx import marshal
from flask_socketio import emit
from .websocket import emit_incident
from .actions import audit_action, incident_action, task_action
from app.models import User, Group, AuditLog, IncidentLog, TaskLog, SupervisorActions
from ..api.utils.models import user_model_without_group, group_model, group_model_without_users, incident_model, point_feature_model


def complete_registration(email_link, firstname, surname, password):
    pattern = re.compile('(?=.*\d)(?=.*[a-z])(?=.*[A-Z])')
    if not pattern.match(password):
        return False
    user = email_link.user
    user.firstname = firstname
    user.surname = surname
    user.set_password(password, initial=True)
    user.status = 1
    db.session.delete(email_link)
    audit_action(user, AuditLog.action_values['verify_user'])


def edit_group(group, name, permissions, changed_by):
    if group.name == name and set(permissions) == set(group.get_permissions()):
        return False
    group.name = name
    group.set_permissions(permissions)
    audit_action(changed_by, AuditLog.action_values['edit_group'])
    emit('edit_group', {'id': group.id, 'name': name, 'permissions': group.get_permissions(), 'code': 200}, namespace='/', room='admin')


def change_user_group(user, group, changed_by):
    if user.group == group:
        return False
    user.group = group
    group_marshalled = marshal(group, group_model_without_users)
    audit_action(changed_by, AuditLog.action_values['edit_user_group'])
    emit('change_user_group', {'id': user.id, 'group': group_marshalled, 'code': 200}, namespace='/', room='admin')

def change_user_status(user, status, changed_by):
    if user.status == status:
        return False
    user.status = status
    audit_action(changed_by, AuditLog.action_values['activate_user' if status == 1 else 'deactivate_user'])
    emit('change_user_status', {'id': user.id, 'status': status, 'code': 200}, namespace='/', room='admin')


def edit_deployment(deployment, name, description, open_status, group_ids, user_ids, changed_by):
    groups = Group.query.filter(Group.id.in_(group_ids)).all()
    users = User.query.filter(User.id.in_(user_ids)).all()
    if deployment.name == name and deployment.description == description and deployment.open_status == open_status and deployment.groups == groups and deployment.users == users:
        return False
    deployment.name = name
    deployment.description = description
    deployment.open_status = open_status
    deployment.groups = groups
    deployment.users = users
    users_marshalled = marshal(deployment.users, user_model_without_group)
    groups_marshalled = marshal(deployment.groups, group_model)
    emit('CHANGE_DEPLOYMENT_EDIT', {'id': deployment.id, 'name': name, 'description': description, 'open': open_status, 'groups': groups_marshalled, 'users': users_marshalled, 'code': 200}, namespace='/', room='deployments')
    audit_action(changed_by, action_type=AuditLog.action_values['edit_deployment'], target_id=deployment.id)
    return deployment


def edit_incident(incident, name, description, incident_type, reported_via, reference, changed_by):
    if incident.name == name and incident.description == description and incident.incident_type == type and incident.reported_via == reported_via and incident.reference == reference:
        return False
    incident.name = name
    incident.description = description
    incident.incident_type = incident_type
    incident.reported_via = reported_via
    incident.reference = reference
    emit_incident('CHANGE_INCIDENT_DETAILS', {'id': incident.id, 'name': name, 'description': description, 'type': incident_type, 'reportedVia': reported_via, 'reference': reference, 'code': 200}, incident)
    incident_action(changed_by, IncidentLog.action_values['edit_incident'], incident=incident)
    return incident


def change_incident_status(incident, status, changed_by):
    if incident.open_status == status:
        return False
    incident.open_status = status
    if status:
        incident.closed_at = None
        action_type = 'marked_incomplete'
    else:
        incident.closed_at = datetime.utcnow()
        action_type = 'marked_complete'
    emit_incident('CHANGE_INCIDENT_STATUS', {'id': incident.id, 'open': status, 'code': 200}, incident)
    incident_action(user=changed_by, action_type=IncidentLog.action_values[action_type], incident=incident)
    actions_required = SupervisorActions.query.filter_by(incident_id=incident.id, action_type='Mark As Complete' if not status else 'Mark As Incomplete').all()
    for x in actions_required:
        supervisor.mark_request_complete(x, False, changed_by)


def change_incident_allocation(incident, allocated_to, changed_by):
    if set(allocated_to) == set(incident.assigned_to):
        return False
    added = list(set(allocated_to) - set(incident.assigned_to))
    removed = list(set(incident.assigned_to) - set(allocated_to))
    incident.assigned_to = allocated_to
    users_marshalled = marshal(incident.assigned_to, user_model_without_group)
    emit_incident('CHANGE_INCIDENT_ALLOCATION', {'id': incident.id, 'assignedTo': users_marshalled, 'code': 200}, incident)
    if removed:
        incident_action(user=changed_by, action_type=IncidentLog.action_values['removed_user'],
                        incident=incident, target_users=removed)
    if added:
        incident_action(user=changed_by, action_type=IncidentLog.action_values['assigned_user'],
                        incident=incident, target_users=added)
    if not incident.supervisor_approved:
        incident.supervisor_approved = True
        incident_marshalled = marshal(incident, incident_model)
        incident_marshalled['pinned'] = False
        for x in incident.assigned_to:
            if not x.has_permission('view_all_incidents'):
                emit('NEW_INCIDENT', {'incident': incident_marshalled, 'code': 200}, namespace='/', room=f'{incident.deployment_id}-{x.id}')
        action_required = SupervisorActions.query.filter_by(incident_id=incident.id, action_type='New Incident').first()
        if action_required:
            supervisor.mark_request_complete(action_required, False, changed_by)


def change_incident_priority(incident, priority, changed_by):
    if incident.priority == priority:
        return False
    incident.priority = priority
    emit_incident('CHANGE_INCIDENT_PRIORITY', {'id': incident.id, 'priority': priority, 'code': 200}, incident)
    incident_action(user=changed_by, action_type=IncidentLog.action_values['changed_priority'],
                    incident=incident, extra=priority)


def change_incident_public(incident, public, name, description, changed_by):
    if (incident.public and public and incident.description == description and incident.name == name) or (not incident.public and not public):
        return False
    incident.public = public
    if public:
        incident.public_name = name
        incident.public_description = description
    emit_incident('CHANGE_INCIDENT_PUBLIC', {'id': incident.id, 'public': public, 'publicName': incident.public_name, 'publicDescription': incident.public_description, 'code': 200}, incident)
    incident_action(user=changed_by, action_type=IncidentLog.action_values['marked_public' if public else 'marked_not_public'],
                    incident=incident)


def change_incident_location(incident, address, longitude, latitude, changed_by):
    if incident.location == address and incident.longitude == longitude and incident.latitude == latitude:
        return False
    incident.location = address
    incident.longitude = longitude
    incident.latitude = latitude
    location_marshalled = marshal(incident, point_feature_model)
    emit_incident('CHANGE_INCIDENT_LOCATION', {'id': incident.id, 'location': location_marshalled, 'code': 200}, incident)
    incident_action(user=changed_by, action_type=IncidentLog.action_values['change_incident_location'], incident=incident)


def change_comment_public(comment, public, changed_by):
    if comment.public == public:
        return False
    comment.public = public
    emit_incident('CHANGE_COMMENT_PUBLIC', {'id': comment.id, 'incidentId': comment.incident.id, 'public': public, 'code': 200},  comment.incident)
    incident_action(user=changed_by, action_type=IncidentLog.action_values['marked_comment_public' if public else 'marked_comment_not_public'],
                    incident=comment.incident, comment=comment)


def change_comment_text(comment, text, changed_by):
    if comment.text == text:
        return False
    comment.text = text
    comment.edited_at = datetime.utcnow()
    emit_incident('CHANGE_COMMENT_TEXT', {'id': comment.id, 'incidentId': comment.incident.id, 'text': text, 'editedAt': comment.edited_at.timestamp(), 'code': 200}, comment.incident)
    incident_action(user=changed_by, action_type=IncidentLog.action_values['edit_comment'],
                    incident=comment.incident, comment=comment)


def change_task_status(task, status, changed_by):
    if task.completed == status:
        return False
    task.completed = status
    if status:
        task.completed_at = datetime.utcnow()
        action_type = 'complete_task'
    else:
        task.completed_at = None
        action_type = 'incomplete_task'
    emit_incident('CHANGE_TASK_STATUS', {'id': task.id, 'incidentId': task.incident.id, 'completed': status, 'timestamp': task.completed_at.timestamp() if task.completed else None, 'code': 200}, task.inciden)
    incident_action(user=changed_by, action_type=IncidentLog.action_values[action_type],
                    incident=task.incident, task=task)


def change_task_description(task, description, changed_by):
    if task.description == description:
        return False
    task.description = description
    emit_incident('CHANGE_TASK_DESCRIPTION', {'id': task.id, 'incidentId': task.incident.id, 'description': description, 'code': 200}, task.incident)
    task_action(user=changed_by, action_type=TaskLog.action_values['changed_description'],
                task=task, extra=description)
    incident_action(user=changed_by, action_type=IncidentLog.action_values['changed_task_description'], incident=task.incident, task=task,
                    extra=description)


def change_task_tags(task, tags, changed_by):
    if (not task.tags and not tags) or (task.tags and tags and set(task.tags) == set(tags)):
        return False
    task.tags = list(set(tags))
    emit_incident('CHANGE_TASK_TAGS', {'id': task.id, 'incidentId': task.incident.id, 'tags': task.tags, 'code': 200}, task.incident)
    task_action(user=changed_by, action_type=TaskLog.action_values['changed_tags'],
                task=task)
    incident_action(user=changed_by, action_type=IncidentLog.action_values['changed_task_tags'], incident=task.incident, task=task)


def change_task_assigned(task, assigned_to, changed_by):
    if set(assigned_to) == set(task.assigned_to):
        return False
    added = list(set(assigned_to) - set(task.assigned_to))
    removed = list(set(task.assigned_to) - set(assigned_to))
    task.assigned_to = assigned_to
    if any([m for m in assigned_to if m not in task.incident.assigned_to]):
        change_incident_allocation(task.incident, assigned_to + task.incident.assigned_to, changed_by)
    users_marshalled = marshal(task.assigned_to, user_model_without_group)
    emit_incident('CHANGE_TASK_ASSIGNED', {'id': task.id, 'incidentId': task.incident.id, 'assignedTo': users_marshalled, 'code': 200}, task.incident)
    if removed:
        task_action(user=changed_by, action_type=TaskLog.action_values['removed_user'], task=task,
                    target_users=removed)
        incident_action(user=changed_by, action_type=IncidentLog.action_values['removed_user_task'],
                        incident=task.incident, task=task, target_users=removed)
    if added:
        task_action(user=changed_by, action_type=TaskLog.action_values['assigned_user'], task=task, target_users=added)
        incident_action(user=changed_by, action_type=IncidentLog.action_values['assigned_user_task'],
                        incident=task.incident, task=task, target_users=added)


def change_task_comment_text(task_comment, text, changed_by):
    if task_comment.text == text:
        return False
    task = task_comment.task
    task_comment.text = text
    task_comment.edited_at = datetime.utcnow()
    emit_incident('CHANGE_TASK_COMMENT_TEXT', {'id': task_comment.id, 'taskId': task.id, 'incidentId': task.incident.id, 'text': text, 'editedAt': task_comment.edited_at.timestamp(), 'code': 200}, task.incident)
    task_action(user=changed_by, action_type=TaskLog.action_values['edit_task_comment'], task=task)
    incident_action(user=changed_by, action_type=IncidentLog.action_values['edit_task_comment'],
                    incident=task.incident, task=task)


def change_subtask_status(subtask, status, changed_by):
    task = subtask.task
    if subtask.completed == status:
        return False
    subtask.completed = status
    if status:
        subtask.completed_at = datetime.utcnow()
        action_type = 'complete_subtask'
    else:
        subtask.completed_at = None
        action_type = 'incomplete_subtask'
    emit_incident('CHANGE_SUBTASK_STATUS', {'id': subtask.id, 'taskId': task.incident.id, 'incidentId': task.incident.id, 'completed': status, 'timestamp': subtask.completed_at.timestamp() if subtask.completed else None, 'code': 200}, task.incident)
    task_action(user=changed_by, action_type=TaskLog.action_values[action_type], task=task, subtask=subtask)
    incident_action(user=changed_by, action_type=IncidentLog.action_values[action_type], incident=task.incident, task=task,
                    extra=subtask.name)
    if len([m for m in task.subtasks if m.completed]) == len(task.subtasks) and not task.completed:
        change_task_status(task, True, changed_by)


def change_subtask(subtask, name, assigned_to, changed_by):
    if subtask.name == name and set(assigned_to) == set(subtask.assigned_to):
        return False
    task = subtask.task
    subtask.name = name
    subtask.assigned_to = assigned_to
    if any([m for m in assigned_to if m not in task.incident.assigned_to]):
        change_incident_allocation(task.incident, assigned_to + task.incident.assigned_to, changed_by)
    if any([m for m in assigned_to if m not in task.assigned_to]):
        change_task_assigned(task, assigned_to + task.assigned_to, changed_by)
    users_marshalled = marshal(subtask.assigned_to, user_model_without_group)
    emit_incident('CHANGE_SUBTASK_EDIT', {'id': subtask.id, 'taskId': task.id, 'incidentId': task.incident.id, 'name': name, 'assignedTo': users_marshalled, 'code': 200}, task.incident.deployment_id)
    task_action(user=changed_by, action_type=TaskLog.action_values['edit_subtask'], task=task, subtask=subtask)
    incident_action(user=changed_by, action_type=IncidentLog.action_values['edit_subtask'], incident=task.incident, task=task,
                    extra=subtask.name)


