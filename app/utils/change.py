from app import db
from datetime import datetime
from collections import Counter
from app.models import User, Incident, IncidentLog


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
    action = IncidentLog(user=user, action_type=IncidentLog.action_values[action_type], incident_id=incident.id)
    db.session.add(action)
    db.session.commit()


def allocation(user, incident, allocated_to_ids):
    allocated_to = User.query.filter(User.id.in_(allocated_to_ids)).all()
    if Counter(allocated_to) == Counter(incident.assigned_to):
        return False
    added = list(set(allocated_to) - set(incident.assigned_to))
    removed = list(set(incident.assigned_to) - set(allocated_to))
    incident.assigned_to = allocated_to
    incident.last_updated = datetime.utcnow()
    if added:
        action = IncidentLog(user=user, action_type=IncidentLog.action_values['assigned_user'],
                             incident_id=incident.id, target_users=added)
        db.session.add(action)
    if removed:
        action = IncidentLog(user=user, action_type=IncidentLog.action_values['removed_user'],
                             incident_id=incident.id, target_users=removed)
        db.session.add(action)
    db.session.commit()


def incident_priority(user, incident, priority):
    if incident.priority == priority:
        return False
    incident.priority = priority
    incident.last_updated = datetime.utcnow()
    action = IncidentLog(user=user, action_type=IncidentLog.action_values['changed_priority'],
                         incident_id=incident.id, extra=Incident.priorities[priority])
    db.session.add(action)
    db.session.commit()


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
    action = IncidentLog(user=user, action_type=IncidentLog.action_values[action_type],
                         incident_id=task.incident.id, task_id=task.id)
    db.session.add(action)
    db.session.commit()
