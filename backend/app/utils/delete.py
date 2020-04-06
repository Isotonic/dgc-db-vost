from app import db
from flask_socketio import emit
from .websocket import emit_incident
from app.models import AuditLog, IncidentLog, TaskLog
from .actions import audit_action, incident_action, task_action

def delete_group(group, deleted_by):
    db.session.delete(group)
    audit_action(user=deleted_by, action_type=AuditLog.action_values['delete_group'])
    emit('delete_group', {'id': group.id, 'code': 200}, namespace='/', room='admin')
    emit('DELETE_USER_GROUP', {'id': group.id, 'code': 200}, namespace='/', room='all')
    emit('DELETE_GROUP', {'id': group.id, 'code': 200}, namespace='/', room='all')


def delete_user(user, deleted_by):
    db.session.delete(user)
    audit_action(user=deleted_by, action_type=AuditLog.action_values['delete_user'])
    emit('delete_user', {'id': user.id, 'code': 200}, namespace='/', room='admin')


def delete_notification(notification):
    db.session.delete(notification)
    db.session.commit()
    emit('delete_notification', {'id': notification.id, 'code': 200}, namespace='/', room=f'{notification.user.id}')


def delete_all_notifications(user):
    for notification in user.notifications:
        db.session.delete(notification)
    db.session.commit()
    emit('delete_all_notifications', {'code': 200}, namespace='/', room=f'{user.id}')


def delete_comment(comment, deleted_by):
    incident = comment.incident
    db.session.delete(comment)
    emit_incident('DELETE_COMMENT', {'id': comment.id, 'incidentId': incident.id, 'code': 200}, incident)
    incident_action(user=deleted_by, action_type=IncidentLog.action_values['delete_comment'], incident=incident)


def delete_task(task, deleted_by):
    incident = task.incident
    db.session.delete(task)
    emit_incident('DELETE_TASK', {'id': task.id, 'incidentId': incident.id, 'code': 200}, incident)
    incident_action(user=deleted_by, action_type=IncidentLog.action_values['delete_task'], incident=incident, extra=task.name)


def delete_subtask(subtask, deleted_by):
    task = subtask.task
    db.session.delete(subtask)
    emit_incident('DELETE_SUBTASK', {'id': subtask.id, 'taskId': task.id, 'incidentId': task.incident.id, 'code': 200}, task.incident)
    task_action(user=deleted_by, action_type=TaskLog.action_values['delete_subtask'], task=task, extra=subtask.name)
    incident_action(user=deleted_by, action_type=IncidentLog.action_values['delete_subtask'], incident=task.incident, task=task, extra=subtask.name)


def delete_task_comment(task_comment, deleted_by):
    task = task_comment.task
    db.session.delete(task_comment)
    emit_incident('DELETE_TASK_COMMENT', {'id': task_comment.id, 'taskId': task.id, 'incidentId': task.incident.id, 'code': 200}, task.incident)
    task_action(user=deleted_by, action_type=TaskLog.action_values['delete_task_comment'], task=task)
    incident_action(user=deleted_by, action_type=IncidentLog.action_values['delete_task_comment'], incident=task.incident, task=task)
