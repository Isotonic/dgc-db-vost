from app import db, moment
from flask_restx import marshal
from flask_socketio import emit
from .actions import incident_action
from .change import change_incident_status
from app.models import SupervisorActions, IncidentLog
from ..api.utils.models import incident_model, action_required_model

def new_action(action, incident):
    action_marshalled = marshal(action, action_required_model)
    emit('NEW_ACTION_REQUIRED', {'action': action_marshalled, 'code': 200}, namespace='', room=f'{incident.deployment_id}-all')


def request_incident_status_change(incident, reason, request_by):
    action = SupervisorActions(deployment_id=incident.deployment_id, incident=incident, action_type='Mark As Incomplete' if not incident.open_status else 'Mark As Complete', reason=reason, requested_by=request_by)
    db.session.add(action)
    db.session.commit()
    new_action(action, incident)
    incident_action(user=request_by, action_type=IncidentLog.action_values['request_mark_incomplete' if not incident.open_status else 'request_mark_complete'], incident=incident)


def flag_to_supervisor(incident, reason, request_by):
    action = SupervisorActions(deployment_id=incident.deployment_id, incident=incident, action_type='Flagged', reason=reason, requested_by=request_by)
    db.session.add(action)
    db.session.commit()
    new_action(action, incident)
    incident_action(user=request_by, action_type=IncidentLog.action_values['flag_supervisor'], incident=incident)


def new_incident(incident, created_by):
    if created_by.has_permission('supervisor'):
        incident_marshalled = marshal(incident, incident_model)
        incident_marshalled['pinned'] = False
        emit('NEW_INCIDENT', {'incident': incident_marshalled, 'code': 200}, namespace='', room=f'{incident.deployment_id}-all')
        return
    action = SupervisorActions(deployment_id=incident.deployment_id, incident=incident, action_type='New Incident', requested_by=created_by)
    db.session.add(action)
    db.session.commit()
    #emit('action_required_count', {'count': incident.deployment.calculate_actions_required(), 'code': 200}, room=f'{incident.deployment_id}-actions-count')
    #emit('new_action_request', {'id': action.id, 'name': incident.name, 'requested_by': str(created_by), 'action_type': action.action_type, 'reason': 'None', 'requested_at': moment.create(action.requested_at).fromNow(refresh=True), 'requested_at_timestamp': action.requested_at.timestamp(), 'code': 200}, room=f'{incident.deployment_id}-actions')


def mark_request_complete(requested_action, change, completed_by):
    incident = requested_action.incident
    if change and ((requested_action.action_type == 'Mark As Complete' and incident.open_status) or ((requested_action.action_type == 'Mark As Incomplete' and not incident.open_status))):
        change_incident_status(incident, not incident.open_status, completed_by)
    if incident.supervisor_approved is False:
        incident.supervisor_approved = True
        incident_marshalled = marshal(incident, incident_model)
        incident_marshalled['pinned'] = False
        emit('NEW_INCIDENT', {'incident': incident_marshalled, 'code': 200}, namespace='', room=f'{incident.deployment_id}-all')
    db.session.delete(requested_action)
    db.session.commit()
    emit('DELETE_ACTION_REQUIRED', {'id': requested_action.id, 'code': 200}, namespace='', room=f'{incident.deployment_id}-all')
