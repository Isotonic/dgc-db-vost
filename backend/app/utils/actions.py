from app import db
from datetime import datetime
from flask_restx import marshal
from .websocket import emit_incident
from app.models import AuditLog, IncidentLog, TaskLog
from ..api.utils.models import activity_model, task_activity_model

def audit_action(user, action_type, target_id=None, reason=None):
    action = AuditLog(user=user, action_type=action_type, target_id=target_id, reason=reason)
    db.session.add(action)
    db.session.commit()

def incident_action(user, action_type, incident, comment=None, task=None, subtask=None, target_users=None, extra=None):
    if not target_users:
        target_users = []
    incident.last_updated = datetime.now()
    action = IncidentLog(user=user, action_type=action_type, incident_id=incident.id, comment=comment, task=task, subtask=subtask, target_users=target_users, extra=extra)
    db.session.add(action)
    db.session.commit()
    action_marshalled = marshal(action, activity_model)
    emit_incident('INCIDENT_ACTIVITY', {'id': incident.id, 'activity': action_marshalled, 'code': 200}, incident)


def task_action(user, action_type, task, subtask=None, target_users=None, extra=None):
    if not target_users:
        target_users = []
    action = TaskLog(user=user, action_type=action_type, task=task, subtask=subtask, target_users=target_users, extra=extra)
    db.session.add(action)
    db.session.commit()
    action_marshalled = marshal(action, task_activity_model)
    emit_incident('TASK_ACTIVITY', {'id': task.id, 'incidentId': task.incident.id, 'activity': action_marshalled, 'code': 200}, task.incident)
