from app import db
from flask_socketio import emit
from flask import render_template
from app.models import IncidentLog

def IncidentAction(user, action_type, incident, task=None, target_users=[], extra=None):
    action = IncidentLog(user=user, action_type=action_type, incident_id=incident.id, task=task, target_users=target_users, extra=extra)
    db.session.add(action)
    db.session.commit()
    emit('activity', {'html': [render_template('action.html', action=action)]}, room=f'{incident.deployment_id}-{incident.id}')
