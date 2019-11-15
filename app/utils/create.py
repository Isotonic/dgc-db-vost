import secrets
from app import db
from app.models import User, Group, Deployment, Incident, IncidentTask, IncidentComment, EmailLink, AuditLog, IncidentLog


def new_user(firstname, surname, email, groupid, created_by):
    user = User(firstname=firstname, surname=surname, email=email, group_id=groupid)
    db.session.add(user)
    db.session.commit()
    user.create_avatar()
    email_link = EmailLink(user_id=user.id, link=secrets.token_urlsafe(20), verify=True)
    db.session.add(email_link)
    action = AuditLog(user=created_by, action_type=AuditLog.action_values['create_user'], target_id=user.id)
    db.session.add(action)
    db.session.commit()
    return user


def new_group(name, permission_list, created_by):
    group = Group(name=name)
    group.set_permissions(permission_list)
    db.session.add(group)
    db.session.commit()
    action = AuditLog(user=created_by, action_type=AuditLog.action_values['create_group'],
                      target_id=group.id)
    db.session.add(action)
    db.session.commit()
    return group


def new_deployment(name, description, group_ids, user_ids, created_by):
    groups = Group.query.filter(Group.id.in_(group_ids)).all()
    users = User.query.filter(User.id.in_(user_ids)).all()
    deployment = Deployment(name=name, description=description, groups=groups, users=users)
    db.session.add(deployment)
    db.session.commit()
    action = AuditLog(user=created_by, action_type=AuditLog.action_values['create_deployment'],
                      target_id=deployment.id)
    db.session.add(action)
    db.session.commit()
    return deployment


def new_incident(name, description, location, deployment, created_by):
    incident = Incident(name=name, description=description, location=location, deployment=deployment)
    db.session.add(incident)
    db.session.commit()
    action = IncidentLog(user=created_by, action_type=IncidentLog.action_values['create_incident'],
                         incident_id=incident.id)
    db.session.add(action)
    db.session.commit()
    return incident

def new_task(name, user_ids, incident, created_by):
    users = User.query.filter(User.id.in_(user_ids)).all()
    task = IncidentTask(name=name, assigned_to=users, incident=incident)
    db.session.add(task)
    db.session.commit()
    action = IncidentLog(user=created_by, action_type=IncidentLog.action_values['create_task'],
                         incident_id=incident.id, target_users=users)
    db.session.add(action)
    db.session.commit()
    return task

def new_comment(text, highlight, incident, added_by):
    comment = IncidentComment(text=text, highlight=highlight, user_id=added_by.id, incident=incident)
    db.session.add(comment)
    db.session.commit()
    action = IncidentLog(user=added_by, action_type=IncidentLog.action_values['add_comment'],
                         incident_id=incident.id)
    db.session.add(action)
    db.session.commit()
    return comment