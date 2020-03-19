from app import db
from datetime import datetime
from flask_restx import marshal
from flask_socketio import emit
from app.models import Notifications
from ..api.utils.models import notification_model

def new_notification(users, reason, action_type, incident, triggered_by):
    for x in users:
        if x == triggered_by:
            continue
        notification = Notifications(user=x, reason=reason, action_type=action_type, deployment=incident.deployment, incident=incident, triggered_by=triggered_by, triggered_at=datetime.utcnow())
        db.session.add(notification)
        notification_marshalled = marshal(notification, notification_model)
        emit('NEW_NOTIFICATION', notification_marshalled, namespace='/', room=f'{x.id}')
    db.session.commit()
