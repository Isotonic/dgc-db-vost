import secrets
from app import db
from app.models import User, Group, Deployment, Incident, EmailLink, AuditLog, IncidentLog


def new_user(username, email, groupid, created_by):
    user = User(username=username, email=email, group_id=groupid)
    db.session.add(user)
    db.session.commit()
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


def new_incident(name, description, location, created_by):
    incident = Incident(name=name, description=description, location=location)
    db.session.add(incident)
    db.session.commit()
    action = IncidentLog(user=created_by, action_type=IncidentLog.action_values['create_incident'],
                         incident_id=incident.id)
    db.session.add(action)
    db.session.commit()
    return incident
