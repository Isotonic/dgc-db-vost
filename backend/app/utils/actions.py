from app import db
from flask_socketio import emit
from flask import render_template
from app.models import IncidentLog, TaskLog

def incident_action(user, action_type, incident, comment=None, task=None, subtask=None, target_users=None, extra=None):
    if not target_users:
        target_users = []
    action = IncidentLog(user=user, action_type=action_type, incident_id=incident.id, comment=comment, task=task, subtask=subtask, target_users=target_users, extra=extra)
    db.session.add(action)
    db.session.commit()
#    emit('activity', {'html': [render_template('action.html', action=action)], 'code': 200}, room=f'{incident.deployment_id}-{incident.id}')

def task_action(user, action_type, task, subtask=None, target_users=None, extra=None):
    if not target_users:
        target_users = []
    action = TaskLog(user=user, action_type=action_type, task=task, subtask=subtask, target_users=target_users, extra=extra)
    db.session.add(action)
    db.session.commit()
#    emit('task_activity', {'html': [render_template('action.html', action=action)], 'code': 200}, room=f'{task.incident.id}-{task.id}')