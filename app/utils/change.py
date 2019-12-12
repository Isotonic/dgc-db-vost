from app import moment
from datetime import datetime
from collections import Counter
from flask_socketio import emit
from flask import render_template
from .actions import IncidentAction
from app.models import Incident, IncidentLog


def incident_status(user, incident, status):
    if incident.open_status == status:
        return False
    incident.open_status = status
    if status:
        incident.closed_at = datetime.utcnow()
        action_type = 'marked_complete'
    else:
        incident.closed_at = None
        action_type = 'marked_incomplete'
    incident.last_updated = datetime.utcnow()
    emit('change_incident_status', {'status': status, 'code': 200}, room=f'{incident.deployment_id}-{incident.id}')
    IncidentAction(user=user, action_type=IncidentLog.action_values[action_type], incident=incident)


def allocation(user, incident, allocated_to):
    if Counter(allocated_to) == Counter(incident.assigned_to):
        return False
    added = list(set(allocated_to) - set(incident.assigned_to))
    removed = list(set(incident.assigned_to) - set(allocated_to))
    incident.assigned_to = allocated_to
    incident.last_updated = datetime.utcnow()
    emit('change_incident_allocation', {'html': [render_template('assigned_to.html', user=m) for m in incident.assigned_to], 'code': 200}, room=f'{incident.deployment_id}-{incident.id}')
    if removed:
        IncidentAction(user=user, action_type=IncidentLog.action_values['removed_user'],
                             incident=incident, target_users=removed)
    if added:
        IncidentAction(user=user, action_type=IncidentLog.action_values['assigned_user'],
                             incident=incident, target_users=added)


def incident_priority(user, incident, priority):
    if incident.priority == priority:
        return False
    incident.priority = priority
    incident.last_updated = datetime.utcnow()
    emit('change_incident_priority', {'priority': Incident.priorities[incident.priority].title(), 'code': 200}, room=f'{incident.deployment_id}-{incident.id}')
    IncidentAction(user=user, action_type=IncidentLog.action_values['changed_priority'],
                         incident=incident, extra=Incident.priorities[priority])


def task_status(user, task, status):
    if task.completed == status:
        return False
    task.completed = status
    if status:
        task.completed_at = datetime.utcnow()
        action_type = 'complete_task'
    else:
        task.completed_at = None
        action_type = 'incomplete_task'
    task.incident.last_updated = datetime.utcnow()
    emit('change_task_status', {'id': task.id, 'completed': task.completed, 'timestamp': moment.create(task.completed_at if task.completed else task.created_at).fromNow(refresh=True), 'code': 200}, room=f'{task.incident.deployment_id}-{task.incident.id}')
    IncidentAction(user=user, action_type=IncidentLog.action_values[action_type],
                         incident=task.incident, task=task)
