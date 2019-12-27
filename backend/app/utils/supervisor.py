from app import db, moment
from flask_socketio import emit
from flask import render_template
from app.models import SupervisorActions

def request_incident_complete(incident, status, reason, request_by):
    if incident.open_status == status:
        return False
    action = SupervisorActions(deployment_id=incident.deployment_id, incident=incident, action_type='Mark As Incomplete' if status else 'Mark As Complete', reason=reason, requested_by=request_by)
    db.session.add(action)
    db.session.commit()
    emit('action_required_count', {'count': incident.deployment.calculate_actions_required(), 'code': 200}, room=f'{incident.deployment_id}-actions-count')
    emit('new_action_request', {'id': action.id, 'name': incident.name, 'requested_by': str(request_by), 'action_type': action.action_type, 'reason': 'None', 'requested_at': moment.create(action.requested_at).fromNow(refresh=True), 'requested_at_timestamp': action.requested_at.timestamp(), 'code': 200}, room=f'{incident.deployment_id}-actions')


def flag_to_supervisor(incident, reason, request_by):
    action = SupervisorActions(deployment_id=incident.deployment_id, incident=incident, action_type='Flagged', reason=reason, requested_by=request_by)
    db.session.add(action)
    db.session.commit()
    emit('action_required_count', {'count': incident.deployment.calculate_actions_required(), 'code': 200}, room=f'{incident.deployment_id}-actions-count')
    emit('new_action_request', {'id': action.id, 'name': incident.name, 'requested_by': str(request_by), 'action_type': action.action_type, 'reason': 'None', 'requested_at': moment.create(action.requested_at).fromNow(refresh=True), 'requested_at_timestamp': action.requested_at.timestamp(), 'code': 200}, room=f'{incident.deployment_id}-actions')


def new_incident(incident, created_by):
    if created_by.has_permission('supervisor'):
        return
    action = SupervisorActions(deployment_id=incident.deployment_id, incident=incident, action_type='New Incident', requested_by=created_by)
    db.session.add(action)
    db.session.commit()
    emit('action_required_count', {'count': incident.deployment.calculate_actions_required(), 'code': 200}, room=f'{incident.deployment_id}-actions-count')
    emit('new_action_request', {'id': action.id, 'name': incident.name, 'requested_by': str(created_by), 'action_type': action.action_type, 'reason': 'None', 'requested_at': moment.create(action.requested_at).fromNow(refresh=True), 'requested_at_timestamp': action.requested_at.timestamp(), 'code': 200}, room=f'{incident.deployment_id}-actions')


def mark_request_complete(requested_action, completed_by):
    requested_action.completed = True
    requested_action.completed_by = completed_by
    incident = requested_action.incident
    if incident.supervisor_approved is False:
        incident.supervisor_approved = True
        emit('create_incident',
             {'name': incident.name, 'location': incident.location, 'priority': incident.priority, 'assigned_to': incident.assigned_to if incident.assigned_to else 'Unassigned',
              'tasks': render_template('percentage.html', incident=incident), 'last_updated': moment.create(incident.last_updated).fromNow(refresh=True), 'last_updated_timestamp': incident.last_updated.timestamp(), 'code': 200},
             room=f'{incident.deployment_id}-all')
    db.session.commit()
    emit('mark_request_complete', {'id': requested_action.id, 'code': 200},
         room=f'{requested_action.deployment_id}-actions')
    emit('action_required_count', {'count': requested_action.deployment.calculate_actions_required(), 'code': 200}, room=f'{requested_action.deployment_id}-actions-count')
