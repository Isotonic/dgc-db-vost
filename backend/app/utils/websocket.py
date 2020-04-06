from flask_socketio import emit
from ..websockets import assigned_rooms

def emit_incident(name, data, incident):
    deployment_id = incident.deployment_id
    emit(name, data, namespace='/', room=f'{deployment_id}-all')

    for x in incident.assigned_to:
        if not x.has_permission('view_all_incidents') and f'{deployment_id}-{x.id}' in assigned_rooms:
            emit(name, data, namespace='/', room=f'{deployment_id}-{x.id}')