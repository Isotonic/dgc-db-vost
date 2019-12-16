from datetime import datetime
from collections import Counter
from flask_socketio import emit
from flask import render_template
from .actions import incident_action, task_action
from app.models import Incident, IncidentLog, TaskLog


def change_incident_status(incident, status, changed_by):
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
    incident_action(user=changed_by, action_type=IncidentLog.action_values[action_type], incident=incident)


def change_allocation(incident, allocated_to, changed_by):
    if Counter(allocated_to) == Counter(incident.assigned_to):
        return False
    added = list(set(allocated_to) - set(incident.assigned_to))
    removed = list(set(incident.assigned_to) - set(allocated_to))
    incident.assigned_to = allocated_to
    incident.last_updated = datetime.utcnow()
    emit('change_incident_allocation',
         {'html': [render_template('assigned_to.html', user=m) for m in incident.assigned_to], 'code': 200},
         room=f'{incident.deployment_id}-{incident.id}')
    if removed:
        incident_action(user=changed_by, action_type=IncidentLog.action_values['removed_user'],
                        incident=incident, target_users=removed)
    if added:
        incident_action(user=changed_by, action_type=IncidentLog.action_values['assigned_user'],
                        incident=incident, target_users=added)


def change_incident_priority(incident, priority, changed_by):
    if incident.priority == priority:
        return False
    incident.priority = priority
    incident.last_updated = datetime.utcnow()
    emit('change_incident_priority', {'priority': Incident.priorities[incident.priority].title(), 'code': 200},
         room=f'{incident.deployment_id}-{incident.id}')
    incident_action(user=changed_by, action_type=IncidentLog.action_values['changed_priority'],
                    incident=incident, extra=Incident.priorities[priority])


def change_task_status(task, status, changed_by):
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
    emit('change_task_status', {'id': task.id, 'completed': task.completed,
                                'timestamp': task.completed_at.timestamp() if task.completed else task.created_at.timestamp(),
                                'code': 200}, room=f'{task.incident.deployment_id}-{task.incident.id}')
    incident_action(user=changed_by, action_type=IncidentLog.action_values[action_type],
                    incident=task.incident, task=task)


def change_task_description(task, description, changed_by):
    if task.description == description:
        return False
    task.description = description
    task.incident.last_updated = datetime.utcnow()
    emit('change_task_description', {'id': task.id, 'description': task.description,
                                     'code': 200}, room=f'{task.incident.deployment_id}-{task.incident.id}')
    incident_action(user=changed_by, action_type=IncidentLog.action_values['changed_task_description'],
                    incident=task.incident, task=task, extra=description)


def change_task_assigned(task, assigned_to, changed_by):
    if Counter(assigned_to) == Counter(task.assigned_to):
        return False
    added = list(set(assigned_to) - set(task.assigned_to))
    removed = list(set(task.assigned_to) - set(assigned_to))
    task.assigned_to = assigned_to
    emit('change_task_assigned',
         {'id': task.id, 'text': task.get_assigned(), 'code': 200},
         room=f'{task.incident.deployment_id}-{task.incident.id}')
    if removed:
        incident_action(user=changed_by, action_type=IncidentLog.action_values['removed_user_task'],
                        incident=task.incident, task=task, target_users=removed)
    if added:
        incident_action(user=changed_by, action_type=IncidentLog.action_values['assigned_user_task'],
                        incident=task.incident, task=task, target_users=added)


def change_subtask_status(subtask, status, changed_by):
    task = subtask.task
    if subtask.completed == status:
        return False
    subtask.completed = status
    if status:
        subtask.completed_at = datetime.utcnow()
        action_type = 'complete_subtask'
    else:
        subtask.completed_at = None
        action_type = 'incomplete_subtask'
    task.incident.last_updated = datetime.utcnow()
    emit('change_subtask_status', {'id': subtask.id, 'completed': subtask.completed,
                                   'timestamp': subtask.completed_at.timestamp() if subtask.completed else subtask.created_at.timestamp(),
                                   'code': 200},
         room=f'{task.incident.deployment_id}-{task.incident.id}')
    task_action(user=changed_by, action_type=TaskLog.action_values[action_type], task=task, subtask=subtask)
    if len([m for m in task.subtasks if m.completed]) == len(task.subtasks) and not task.completed:
        change_task_status(task, True, changed_by)
