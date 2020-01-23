import secrets
from app import db
from flask_socketio import emit
from flask import render_template
from .supervisor import new_incident
from .change import change_task_status
from .actions import incident_action, task_action
from app.models import User, Group, Deployment, Incident, IncidentTask, IncidentSubTask, TaskComment, IncidentComment, EmailLink, AuditLog, IncidentLog, TaskLog


def create_user(firstname, surname, email, groupid, created_by):
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


def create_group(name, permission_list, created_by):
    group = Group(name=name)
    group.set_permissions(permission_list)
    db.session.add(group)
    db.session.commit()
    action = AuditLog(user=created_by, action_type=AuditLog.action_values['create_group'],
                      target_id=group.id)
    db.session.add(action)
    db.session.commit()
    return group


def create_deployment(name, description, group_ids, user_ids, created_by):
    groups = Group.query.filter(Group.id.in_(group_ids)).all()
    users = User.query.filter(User.id.in_(user_ids)).all()
    deployment = Deployment(name=name, description=description, groups=groups, users=users)
    db.session.add(deployment)
    db.session.commit()
    emit('create_deployment', {'html': render_template('deployment_card.html', deployment=deployment), 'code': 200}, room='deployments')
    action = AuditLog(user=created_by, action_type=AuditLog.action_values['create_deployment'],
                      target_id=deployment.id)
    db.session.add(action)
    db.session.commit()
    return deployment


def create_incident(name, description, incident_type, location, longitude, latitude, reported_via, reference, deployment, created_by):
    incident = Incident(name=name, description=description, supervisor_approved=created_by.has_permission('supervisor'), priority='Standard', incident_type=incident_type, location=location, longitude=longitude, latitude=latitude, reported_via=reported_via,
                        reference=reference, deployment=deployment, created_by=created_by.id)
    db.session.add(incident)
    db.session.commit()
    incident_action(user=created_by, action_type=IncidentLog.action_values['create_incident'],
                   incident=incident)
    new_incident(incident, created_by)
    return incident


def create_task(name, users, description, incident, created_by):
    task = IncidentTask(name=name, assigned_to=users, description=description, incident=incident)
    db.session.add(task)
    db.session.commit()
    emit('create_incident_task', {'html': render_template('task.html', task=task), 'code': 200},
         room=f'{incident.deployment_id}-{incident.id}')
    incident_action(user=created_by, action_type=IncidentLog.action_values['create_task'],
                   incident=incident, task=task, target_users=users)
    return task


def create_subtask(name, users, task, created_by):
    subtask = IncidentSubTask(name=name, assigned_to=users, task=task)
    db.session.add(task)
    db.session.commit()
    #emit('create_incident_task', {'html': render_template('task.html', task=task), 'code': 200},
    #     room=f'{task.incident.deployment_id}-{task.incident.id}')
    task_action(user=created_by, action_type=TaskLog.action_values['create_subtask'], task=task, subtask=subtask, target_users=users)
    incident_action(user=created_by, action_type=IncidentLog.action_values['create_subtask'], incident=task.incident, task=task, extra=subtask.name)
    if len([m for m in task.subtasks if m.completed]) != len(task.subtasks) and  task.completed:
        change_task_status(task, False, created_by)
    emit('create_incident_subtask', {'html': render_template('subtask.html', subtask=subtask), 'code': 200}, room=f'{task.incident.id}-{task.id}')
    return task


def create_task_comment(text, task, added_by):
    comment = TaskComment(text=text, user=added_by, task=task)
    db.session.add(comment)
    db.session.commit()
    emit('create_task_comment', {'html': render_template('comment.html', comment=comment), 'code': 200},
         room=f'{task.incident.id}-{task.id}')
    task_action(user=added_by, action_type=TaskLog.action_values['add_comment'],
                   task=task)
    incident_action(user=added_by, action_type=IncidentLog.action_values['add_subtask_comment'], incident=task.incident, task=task)
    return comment


def create_comment(text, incident, added_by):
    comment = IncidentComment(text=text, user_id=added_by.id, incident=incident)
    db.session.add(comment)
    db.session.commit()
    #emit('create_incident_comment', {'html': render_template('comment.html', comment=comment), 'code': 200},
    #     room=f'{incident.deployment_id}-{incident.id}')
    incident_action(user=added_by, action_type=IncidentLog.action_values['add_comment'],
                   incident=incident)
    return comment
