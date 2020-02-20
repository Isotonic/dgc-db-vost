from app import db
from flask_socketio import emit
from app.models import AuditLog, IncidentLog, TaskLog
from .actions import audit_action, incident_action, task_action

def delete_group(group, deleted_by):
    db.session.delete(group)
    audit_action(user=deleted_by, action_type=AuditLog.action_values['delete_group'])


def delete_user(user, deleted_by):
    db.session.delete(user)
    audit_action(user=deleted_by, action_type=AuditLog.action_values['delete_user'])


def delete_comment(comment, deleted_by):
    incident = comment.incident
    db.session.delete(comment)
    emit('DELETE_COMMENT', {'id': comment.id, 'incidentId': incident.id, 'code': 200}, namespace='', room=f'{incident.deployment_id}-all')
    incident_action(user=deleted_by, action_type=IncidentLog.action_values['delete_comment'], incident=incident)


def delete_task(task, deleted_by):
    incident = task.incident
    db.session.delete(task)
    emit('DELETE_TASK', {'id': task.id, 'incidentId': incident.id, 'code': 200}, namespace='', room=f'{incident.deployment_id}-all')
    incident_action(user=deleted_by, action_type=IncidentLog.action_values['delete_task'], incident=incident)


def delete_subtask(subtask, deleted_by):
    task = subtask.task
    db.session.delete(subtask)
    emit('DELETE_SUBTASK', {'id': subtask.id, 'taskId': task.id, 'incidentId': task.incident.id, 'code': 200}, namespace='', room=f'{task.incident.deployment_id}-all')
    task_action(user=deleted_by, action_type=TaskLog.action_values['delete_subtask'], task=task, extra=subtask.name)
    incident_action(user=deleted_by, action_type=IncidentLog.action_values['delete_subtask'], incident=task.incident, task=task)


def delete_task_comment(task_comment, deleted_by):
    task = task_comment.task
    db.session.delete(task_comment)
    emit('DELETE_TASK_COMMENT', {'id': task_comment.id, 'taskId': task.id, 'incidentId': task.incident.id, 'code': 200}, namespace='', room=f'{task.incident.deployment_id}-all')
    task_action(user=deleted_by, action_type=TaskLog.action_values['delete_task_comment'], task=task)
    incident_action(user=deleted_by, action_type=IncidentLog.action_values['delete_task_comment'], incident=task.incident, task=task)
