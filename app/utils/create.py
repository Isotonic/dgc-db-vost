import secrets
from app import db
from app.models import User, Group, EmailLink, ActionLog


def new_user(username, email, groupid, created_by):
    user = User(username=username, email=email, group_id=groupid)
    db.session.add(user)
    db.session.commit()
    email_link = EmailLink(user_id=user.id, link=secrets.token_urlsafe(20), verify=True)
    db.session.add(email_link)
    action = ActionLog(user=created_by, action_type=ActionLog.action_values["create_user"], target_id=user.id)
    db.session.add(action)
    db.session.commit()
    return user


def new_group(name, permission_list, created_by):
    group = Group(name=name)
    group.set_permissions(permission_list)
    db.session.add(group)
    db.session.commit()
    action = ActionLog(user=created_by, action_type=ActionLog.action_values["create_group"],
                       target_id=group.id)
    db.session.add(action)
    db.session.commit()
    return group
