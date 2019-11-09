from app import db
from datetime import datetime
from app.models import IncidentLog

def task_status(user, task, status):
    task.completed = status
    task.incident.last_updated = datetime.utcnow()
    action = IncidentLog(user=user, action_type=IncidentLog.action_values['complete_task'] if status else IncidentLog.action_values['incomplete_task'],
                         incident_id=task.incident.id, task_id=task.id)
    db.session.add(action)
    db.session.commit()
