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
    incident_action(user=deleted_by, action_type=IncidentLog.action_values['delete_comment'], incident=incident)


def delete_task(task, deleted_by):
    incident = task.incident
    db.session.delete(task)
    #emit('delete_subtask', {'id': subtask.id, 'code': 200},
    #     room=f'{task.incident.deployment_id}-{task.incident.id}-{task.id}')
    incident_action(user=deleted_by, action_type=IncidentLog.action_values['delete_task'], incident=incident)


def delete_subtask(subtask, deleted_by):
    task = subtask.task
    db.session.delete(subtask)
    #emit('delete_subtask', {'id': subtask.id, 'code': 200},
    #     room=f'{task.incident.deployment_id}-{task.incident.id}-{task.id}')
    task_action(user=deleted_by, action_type=TaskLog.action_values['delete_subtask'], task=task, extra=subtask.name)
