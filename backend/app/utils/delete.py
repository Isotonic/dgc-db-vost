from app import db
from flask_socketio import emit
from app.models import IncidentLog, TaskLog
from .actions import incident_action, task_action


def delete_comment(comment, deleted_by):
    incident = comment.incident
    db.session.delete(comment)
    incident_action(user=deleted_by, action_type=IncidentLog.action_values['delete_comment'], incident=incident)


def delete_subtask(subtask, deleted_by):
    task = subtask.task
    db.session.delete(subtask)
    emit('delete_subtask', {'id': subtask.id, 'code': 200},
         room=f'{task.incident.deployment_id}-{task.incident.id}-{task.id}')
    task_action(user=deleted_by, action_type=TaskLog.action_values['delete_subtask'], task=subtask.task, extra=subtask.name)
