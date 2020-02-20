import secrets
from app import db
from flask_restx import marshal
from flask_socketio import emit
from .supervisor import new_incident
from .change import change_task_status
from .actions import audit_action, incident_action, task_action
from ..api.utils.models import deployment_model, comment_model, task_model, task_comment_model, subtask_model
from app.models import User, Group, Deployment, Incident, IncidentTask, IncidentSubTask, TaskComment, IncidentComment, EmailLink, AuditLog, IncidentLog, TaskLog


def create_user(email, group, created_by):
    if email == '':
        return False
    user = User(email=email, group=group)
    db.session.add(user)
    db.session.commit()
    email_link = EmailLink(user_id=user.id, link=secrets.token_urlsafe(20), verify=True)
    db.session.add(email_link)
    audit_action(created_by, action_type=AuditLog.action_values['create_user'], target_id=user.id)
    email_link.send_registration_email()
    return user


def create_group(name, permission_list, created_by):
    if name == '':
        return False
    group = Group(name=name)
    group.set_permissions(permission_list)
    db.session.add(group)
    db.session.commit()
    audit_action(created_by, action_type=AuditLog.action_values['create_group'], target_id=group.id)
    return group


def create_deployment(name, description, group_ids, user_ids, created_by):
    if name == '' or description == '':
        return False
    groups = Group.query.filter(Group.id.in_(group_ids)).all()
    users = User.query.filter(User.id.in_(user_ids)).all()
    deployment = Deployment(name=name, description=description, groups=groups, users=users)
    db.session.add(deployment)
    db.session.commit()
    deployment_marshalled = marshal(deployment, deployment_model)
    emit('NEW_DEPLOYMENT', {'deployment': deployment_marshalled, 'code': 200}, namespace='', room=f'deployments')
    audit_action(created_by, action_type=AuditLog.action_values['create_deployment'], target_id=deployment.id)
    return deployment


def create_incident(deployment, name, description, incident_type, reported_via, reference, address, longitude, latitude, created_by):
    if name == '':
        return False
    incident = Incident(name=name, description=description, supervisor_approved=created_by.has_permission('supervisor'), priority='Standard', incident_type=incident_type, location=address, longitude=longitude, latitude=latitude, reported_via=reported_via,
                        reference=reference, deployment=deployment, created_by=created_by.id)
    db.session.add(incident)
    db.session.commit()
    incident_action(user=created_by, action_type=IncidentLog.action_values['create_incident'],
                   incident=incident)
    new_incident(incident, created_by)
    return incident


def create_comment(text, public, incident, added_by):
    if text == '':
        return False
    comment = IncidentComment(text=text, public=public, user_id=added_by.id, incident=incident)
    db.session.add(comment)
    db.session.commit()
    comment_marshalled = marshal(comment, comment_model)
    emit('NEW_COMMENT', {'id': incident.id, 'comment': comment_marshalled, 'code': 200}, namespace='', room=f'{incident.deployment_id}-all')
    incident_action(user=added_by, action_type=IncidentLog.action_values['add_comment'],
                   incident=incident)
    return comment


def create_task(name, users, description, incident, created_by):
    if name == '':
        return False
    task = IncidentTask(name=name, assigned_to=users, description=description, incident=incident)
    db.session.add(task)
    db.session.commit()
    task_marshalled = marshal(task, task_model)
    emit('NEW_TASK', {'id': incident.id, 'task': task_marshalled, 'code': 200}, namespace='', room=f'{incident.deployment_id}-all')
    incident_action(user=created_by, action_type=IncidentLog.action_values['create_task'],
                   incident=incident, task=task, target_users=users)
    return task


def create_subtask(name, users, task, created_by):
    if name == '':
        return False
    subtask = IncidentSubTask(name=name, assigned_to=users, task=task)
    db.session.add(task)
    db.session.commit()
    subtask_marshalled = marshal(subtask, subtask_model)
    emit('NEW_SUBTASK', {'id': task.id, 'incidentId': task.incident.id, 'subtask': subtask_marshalled, 'code': 200}, namespace='', room=f'{task.incident.deployment_id}-all')
    task_action(user=created_by, action_type=TaskLog.action_values['create_subtask'], task=task, subtask=subtask, target_users=users)
    incident_action(user=created_by, action_type=IncidentLog.action_values['create_subtask'], incident=task.incident, task=task, extra=subtask.name)
    if len([m for m in task.subtasks if m.completed]) != len(task.subtasks) and  task.completed:
        change_task_status(task, False, created_by)
    return task


def create_task_comment(text, task, added_by):
    if task == '':
        return False
    comment = TaskComment(text=text, user=added_by, task=task)
    db.session.add(comment)
    db.session.commit()
    comment_marshalled = marshal(comment, task_comment_model)
    emit('NEW_TASK_COMMENT', {'id': task.id, 'incidentId': task.incident.id, 'comment': comment_marshalled, 'code': 200}, namespace='', room=f'{task.incident.deployment_id}-all')
    task_action(user=added_by, action_type=TaskLog.action_values['add_comment'],
                   task=task)
    incident_action(user=added_by, action_type=IncidentLog.action_values['add_subtask_comment'], incident=task.incident, task=task)
    return comment