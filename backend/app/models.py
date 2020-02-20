import pyavagen
from flask import url_for
from string import Template
from threading import Thread
from os import path, makedirs
from flask_admin import Admin  ##TODO Remove
from flask_mail import Message
from mailjet_rest import Client
from flask import render_template
from flask_login import UserMixin
from datetime import datetime, timedelta
from flask_admin.contrib.sqla import ModelView
from app import app, db, login, argon2, moment, mail

avatar_colours = ['#26de81', '#3867d6', '#eb3b5a', '#0fb9b1', '#f7b731', '#a55eea', '#fed330', '#45aaf2', '#fa8231',
                  '#2bcbba', '#fd9644', '#2d98da', '#8854d0', '#20bf6b', '#fc5c65', '#4b7bec']

deployment_user_junction = db.Table('deployment_users',
                                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                    db.Column('deployment_id', db.Integer, db.ForeignKey('deployment.id')),
                                    )

deployment_group_junction = db.Table('deployment_groups',
                                     db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
                                     db.Column('deployment_id', db.Integer, db.ForeignKey('deployment.id')),
                                     )

incident_user_junction = db.Table('incident_users',
                                  db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                  db.Column('incident_id', db.Integer, db.ForeignKey('incident.id')),
                                  )

incident_pinned_junction = db.Table('incident_pins',
                                    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                    db.Column('incident_id', db.Integer, db.ForeignKey('incident.id')),
                                    )

incidenttask_user_junction = db.Table('task_users',
                                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                      db.Column('id', db.Integer, db.ForeignKey('incident_task.id')),
                                      )

incidentsubtask_user_junction = db.Table('subtask_users',
                                         db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                         db.Column('id', db.Integer, db.ForeignKey('incident_sub_task.id')),
                                         )

incidentlog_target_users_junction = db.Table('incidentlog_target_users_actions',
                                             db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                             db.Column('id', db.Integer, db.ForeignKey('incident_log.id')),
                                             )

tasklog_target_users_junction = db.Table('tasklog_target_users_actions',
                                         db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                         db.Column('id', db.Integer, db.ForeignKey('task_log.id')),
                                         )


def list_of_names(names):
    if not names:
        return None
    elif len(names) == 1:
        return str(names[0])
    return f'{", ".join([str(m) for m in names[:-1]])} and {str(names[-1])}'


def task_string(tasks):
    if not tasks:
        return
    completed = [m for m in tasks if m.completed]
    return f'{len(completed)}/{len(tasks)}'

def async_decorator(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

@async_decorator
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    status = db.Column(db.Integer(), default=0)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group', backref='users')
    email_links = db.relationship('EmailLink', backref='user', cascade='all,delete')
    audit_actions = db.relationship('AuditLog', backref='user', lazy=True)
    incident_comments = db.relationship('IncidentComment', backref='user')
    media_uploads = db.relationship('IncidentMedia', backref='uploaded_by')

    def set_password(self, password, initial=False):
        self.password_hash = argon2.generate_password_hash(password)
        if initial:
            self.password_last_updated = datetime.utcnow()

    def check_password(self, password):
        return argon2.check_password_hash(self.password_hash, password)

    def create_avatar(self):
        if not path.exists(f'./app/static/img/avatars'):  ##TODO Move this to the start-up.
            makedirs(f'./app/static/img/avatars')
        avatar = pyavagen.Avatar(pyavagen.CHAR_AVATAR, size=128, font_size=65,
                                 string=f'{self.firstname} {self.surname}', color_list=avatar_colours)
        avatar.generate().save(f'./app/static/img/avatars/{self.id}_{self.firstname}_{self.surname}.png')

    def get_avatar(self, static=True):
        return 'https://i.imgur.com/m4Klh5p.png'
        try:
            avatar_path = f'{"/static/" if static else ""}img/avatars/{self.id}_{self.firstname}_{self.surname}.png'
            if path.exists(f'./app{avatar_path}'):
                return f'http://localhost:5000{avatar_path}'
            self.create_avatar()
            return f'http://localhost:5000{avatar_path}'
        except: ##TODO FIX: Store in docker volume
           pass

    def get_deployments(self):
        deployments = []
        for x in Deployment.query.all():
            if self.has_deployment_access(x):
                deployments.append(x)
        return deployments

    def get_incidents(self, deployment, open_only=False, closed_only=False, ignore_permissions=False):
        incidents = []
        if not isinstance(deployment, Deployment):
            deployment = Deployment.query.filter_by(id=deployment).first()
        if not deployment:
            return False
        if not self.has_deployment_access(deployment):
            return incidents
        if not ignore_permissions and self.has_permission('view_all_incidents'):
            if open_only:
                return [m for m in deployment.incidents if m.open_status and m.supervisor_approved]
            elif closed_only:
                return [m for m in deployment.incidents if not m.open_status and m.supervisor_approved]
            else:
                return deployment.incidents
        for x in deployment.incidents:
            if ((not open_only and not closed_only) or (open_only and x.open_status) or (closed_only and not x.open_status)) and self in x.assigned_to and x.supervisor_approved:
                incidents.append(x)
        return incidents

    def has_permission(self, permission):
        if self.status != 1:
            return False
        if not self.group:
            return False
        return self.group.has_permission(permission)

    def has_deployment_access(self, deployment):
        if self.status != 1:
            return False
        if not isinstance(deployment, Deployment):
            deployment = Deployment.query.filter_by(id=deployment).first()
        if not deployment:
            return False
        if self.has_permission('supervisor') or (not deployment.groups and not deployment.users) or self in deployment.users:
            return True
        for x in deployment.groups:
            if x.id == self.group_id:
                return True

    def has_incident_access(self, incident):
        if self.status != 1:
            return False
        if not isinstance(incident, Incident):
            incident = Incident.query.filter_by(id=incident).first()
        if not incident:
            return False
        if not self.has_deployment_access(incident.deployment_id):
            return False
        if self.has_permission('view_all_incidents') or self in incident.assigned_to:
            return True
        return False


    def __repr__(self):
        return f'{self.firstname} {self.surname}'


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Group(db.Model):
    permission_values = {'view_all_incidents': 1, 'change_status': 2, 'change_allocation': 4,
                         'mark_as_public': 8,
                         'new_reports': 16, 'create_deployment': 32, 'decision_making_log': 64,
                         'supervisor': 128, 'change_priority': 256}  ##TODO RE-DORDER ONCE DONE AND REMOVE NEW_REPORTS

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    deployments = db.relationship('Deployment', secondary=deployment_group_junction, backref='groups')
    permissions = db.Column(db.Integer)

    def set_permissions(self, permission_list):
        permission_value = 0
        for item in permission_list:
            try:
                permission_value += self.permission_values[item.lower()]
            except ValueError:
                pass
        self.permissions = int(permission_value)

    def get_permissions(self):
        permissions = []
        for key, value in self.permission_values.items():
            if self.permissions & value > 0:
                permissions.append(key)
        return permissions

    def has_permission(self, permission):
        if self.permissions == self.permission_values['supervisor']:
            return True
        try:
            if self.permissions & self.permission_values[permission.lower()] > 0:
                return True
            return False
        except KeyError:
            return False

    def __repr__(self):
        return self.name


class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.String(256))
    open_status = db.Column(db.Boolean(), default=True)
    incidents = db.relationship('Incident', backref='deployment')
    users = db.relationship('User', secondary=deployment_user_junction, backref='deployments')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def name_check(self, deployment_name):
        return self.name.lower() == deployment_name.lower()

    def calculate_actions_required(self):
        return len(SupervisorActions.query.filter_by(deployment_id=self.id, completed=False).all())

    def calculate_incidents_stat(self, user=None):
        if user:
            incidents = user.get_incidents(self)
        else:
            incidents = self.incidents
        two_hours = len([m for m in incidents if (datetime.utcnow() - timedelta(hours=2)) <= m.created_at < (
                datetime.utcnow() - timedelta(hours=1))])
        one_hour = len([m for m in incidents if m.created_at >= (datetime.utcnow() - timedelta(hours=1))])
        if two_hours == one_hour:
            return ['primary', None, 0]
        elif one_hour > two_hours:
            return ['danger', 'plus', one_hour - two_hours]
        else:
            return ['success', 'minus', two_hours - one_hour]

    def __repr__(self):
        return f'{self.name}'


class Incident(db.Model):
    priority_colours = {'Standard': 'yellow', 'Prompt': 'orange', 'Immediate': 'orange-dark'}
    ##TODO Should really load these from a file.
    incident_types = {'Road Incident': 'car', 'Rail Incident': 'subway', 'Aviation Incident': 'plane',
                      'Maritane Incident': 'ship', 'Snow/Ice': 'snowflake',
                      'Severe Wind': 'wind', 'Rain / Flooding': 'cloud-showers-heavy', 'Industrial': 'industry',
                      'Major Accident Hazard Pipeline': '',
                      'Nuclear Incident': 'radiation', 'Fire/Explosion': 'fire', 'Building Collapse': 'building',
                      'Reservoir': '', 'Fuel Disruption': 'gas-pump',
                      'Power Outage': 'plug', 'Gas Supply Interruption': '', 'Public Water Supply': 'water',
                      'Private Water Supply': 'water', 'Telecoms Outage': 'phone-slash',
                      'Blackstart': '', 'Pandemic': '', 'Food Contamination': 'utensils',
                      'Exotic Notification Disease': '', 'Terrorism': '', 'Cyber Attack': '', 'Public Disorder': '',
                      'Protest': '', 'Fatalities': '', 'Casualties': 'first-aid', 'Missing Person(s)': 'user',
                      'Rescue Required': '', 'Evacuation': '', 'Rest Centre Activation': '',
                      'Survivor Reception Centre Activation': '', 'Friends & Family Reception Centre Activation': '',
                      'Humanitarian Assistance Centre Activation': '', 'Casualty Bureau Activation': '',
                      'General Welfare Provision': '', 'Vaccination': '', 'Press Release': 'newspaper',
                      'SitRep Required': 'file', 'Social Media': 'hashtag', 'DGVOST Activation': '', 'Control Zones': '',
                      'Surveillance Zones': 'video',
                      'Movement Restrictions': '', 'Cull': '', 'Disposal': '', 'Disinfection': '', 'Animal Welfare': '',
                      'Plume': '', 'Radiation Pollution': 'radiation-alt', 'Hazardous Chemical Pollution': '',
                      'Oil Pollution': '', 'Sewage / Slurry': ''}

    # TODO Add who has this pinned.
    id = db.Column(db.Integer, primary_key=True, index=True)
    deployment_id = db.Column(db.Integer, db.ForeignKey('deployment.id'))
    name = db.Column(db.String(64), index=True)
    public_name = db.Column(db.String(64))
    description = db.Column(db.String(256))
    public_description = db.Column(db.String(256))
    reported_via = db.Column(db.String(256))
    reference = db.Column(db.String(128))  ##TODO MAYBE CHANGE TO INT
    incident_type = db.Column(db.String(32))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by_user = db.relationship('User', backref='created_incidents')
    closed_at = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    public = db.Column(db.Boolean(), default=False)
    supervisor_approved = db.Column(db.Boolean(), default=False)
    flagged = db.Column(db.Boolean(), default=False)
    open_status = db.Column(db.Boolean(), default=True)
    location = db.Column(db.String(128), index=True)
    priority = db.Column(db.String(10))
    longitude = db.Column(db.Float())
    latitude = db.Column(db.Float())
    assigned_to = db.relationship('User', secondary=incident_user_junction, lazy='selectin', backref='incidents')
    users_pinned = db.relationship('User', secondary=incident_pinned_junction, lazy='selectin', backref='pinned')
    tasks = db.relationship('IncidentTask', backref='incident', lazy='selectin')
    comments = db.relationship('IncidentComment', backref='incident', lazy='selectin')
    medias = db.relationship('IncidentMedia', backref='incident', lazy='selectin')
    actions = db.relationship('IncidentLog', backref='incident', lazy='selectin')

    def name_check(self, deployment_name, incident_name):
        return self.deployment.name.lower() == deployment_name.lower() and self.name.lower() == incident_name.lower()

    def calculate_task_percentage(self):
        if not self.tasks:
            return
        return int((sum([1 for m in self.tasks if m.completed]) / len(self.tasks)) * 100)

    def task_string(self):
        return task_string(self.tasks)

    def get_icon(self):
        if self.incident_type in self.incident_types and self.incident_types[self.incident_type] != '':
            return self.incident_types[self.incident_type]
        return 'exclamation'

    def public_comments(self):
        return [m for m in self.comments if m.public]

    def get_coordinates(self):
        return [self.longitude, self.latitude]

    def get_last_public_updated_at(self):
        last_public_update = 0
        for x in self.comments:
            if x.public:
                if x.edited_at and x.edited_at.timestamp() > last_public_update:
                    last_public_update = x.edited_at.timestamp()
                elif x.sent_at.timestamp() > last_public_update:
                    last_public_update = x.sent_at.timestamp()
        if last_public_update > 0:
            return last_public_update
        return None


class IncidentTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    name = db.Column(db.String(64))
    description = db.Column(db.String(1024))
    tags = db.Column(db.ARRAY(db.String(64)))
    subtasks = db.relationship('IncidentSubTask', backref='task', lazy='selectin', cascade='all,delete')
    comments = db.relationship('TaskComment', backref='task', lazy='selectin', cascade='all,delete')
    completed = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    assigned_to = db.relationship('User', secondary=incidenttask_user_junction, lazy='selectin', backref='tasks')

    def get_assigned(self):
        return list_of_names(self.assigned_to)

    def get_subtasks(self):
        return sorted([{'id': m.id, 'name': m.name, 'completed': m.completed, 'assigned_to': m.get_assigned(),
                        'timestamp': moment.create(m.completed_at if m.completed else m.created_at).fromNow(
                            refresh=True)} for m in self.subtasks], key=lambda k: k['id'])

    def get_comments(self):
        return sorted([{'user': str(m.user), 'user_avatar': m.user.get_avatar(), 'text': str(m),
                        'timestamp': moment.create(m.sent_at).fromNow(refresh=True)} for m in self.comments],
                      key=lambda k: k['timestamp'], reverse=True)

    def get_actions(self):
        return sorted([{'user': str(m.user), 'user_avatar': m.user.get_avatar(), 'text': str(m),
                        'timestamp': moment.create(m.occurred_at).fromNow(refresh=True)} for m in self.task_logs],
                      key=lambda k: k['timestamp'], reverse=True)

    def subtask_string(self):
        return task_string(self.subtasks)

    def __repr__(self):
        return f'{self.name}'


class IncidentSubTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('incident_task.id'))
    name = db.Column(db.String(64))
    completed = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    assigned_to = db.relationship('User', secondary=incidentsubtask_user_junction, lazy='selectin', backref='subtasks')

    def get_assigned(self):
        return list_of_names(self.assigned_to)

    def __repr__(self):
        return f'{self.name}'


class TaskComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('incident_task.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='task_comments', lazy='selectin')
    text = db.Column(db.String())
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'{self.text}'


class IncidentComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String())
    public = db.Column(db.Boolean(), default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'{self.text}'


class IncidentMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    saved_as = db.Column(db.String(64))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class SupervisorActions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deployment_id = db.Column(db.Integer, db.ForeignKey('deployment.id'))
    deployment = db.relationship('Deployment', backref='actions_required')
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    incident = db.relationship('Incident', backref='actions_required')
    requested_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    requested_by = db.relationship('User', backref='actions_requested')
    action_type = db.Column(db.String(64))
    reason = db.Column(db.String(1024))
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)


class EmailLink(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    link = db.Column(db.String(128), unique=True)
    verify = db.Column(db.Boolean(), default=False)
    forgot_password = db.Column(db.Boolean(), default=False)

    def send_registration_email(self):
        msg = Message('DGVOST Registration', sender=app.config.get('MAIL_USERNAME'), recipients=[self.user.email])
        msg.html = render_template('registration_email.html', email_link=self.link)
        send_async_email(app, msg)


class AuditLog(db.Model):
    action_values = {'create_user': 1, 'verify_user': 2, 'edit_user_group': 3, 'edit_user_status': 4, 'delete_user': 5, 'create_group': 6,
                     'edit_group': 7, 'delete_group': 8, 'create_deployment': 9, 'edit_deployment': 10}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action_type = db.Column(db.Integer())
    target_id = db.Column(db.Integer)
    reason = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class IncidentLog(db.Model):
    action_values = {'create_incident': 1, 'create_task': 2, 'complete_task': 3, 'delete_task': 4, 'add_comment': 5,
                     'delete_comment': 6, 'incomplete_task': 7, 'assigned_user': 8, 'removed_user': 9,
                     'marked_complete': 10, 'marked_incomplete': 11, 'changed_priority': 12,
                     'changed_task_description': 13, 'assigned_user_task': 14,
                     'removed_user_task': 15, 'marked_public': 16, 'marked_not_public': 17, 'complete_subtask': 18, 'incomplete_subtask': 19, 'create_subtask': 20, 'add_subtask_comment': 21,
                     'marked_comment_public': 22, 'marked_comment_not_public': 23, 'edit_comment': 24, 'edit_subtask': 25, 'edit_incident': 26, 'changed_task_tags': 27, 'edit_task_comment': 28,
                     'delete_task_comment': 29, 'delete_subtask': 30, 'change_incident_location': 31, 'flag_supervisor': 32, 'request_mark_complete': 33, 'request_mark_incomplete': 34}  ##TODO RE-ORDER ONCE DONE
    action_strings = {1: 'created incident', 2: 'created task $task', 3: 'marked $task as complete',
                      4: 'deleted task $task',
                      5: 'added an update', 6: 'deleted an update', 7: 'marked $task as incomplete',
                      8: 'assigned $target_users to incident',
                      9: 'removed $target_users from incident', 10: 'marked incident as complete',
                      11: 'marked incident as incomplete', 12: 'changed priority to $extra',
                      13: 'changed $task description to "$extra"', 14: 'added $target_users to $task',
                      15: 'removed $target_users from $task', 16: 'set the incident to publicly viewable', 17: 'set the incident to private', 18: 'marked $extra as complete', 19: 'marked $extra as incomplete', 20: 'created sub-task $extra', 21: 'added comment to $task',
                      22: 'marked comment as publicly viewable', 23: 'marked comment as not publicly viewable', 24: 'edited update', 25: 'edited subtask $extra', 26: 'edited incident details', 27: 'changed tags for $task', 28: 'edited comment in $task', 29: 'deleted comment in $task', 30: 'deleted sub-task in $task',
                      31: 'changed the incident location', 32: 'flagged the incident to a supervisor', 33: 'requested the incident be marked as complete', 34: 'requested the incident be marked as incomplete'}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='incident_actions')
    incident_id = db.Column(db.Integer, db.ForeignKey('incident.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('incident_comment.id'))
    comment = db.relationship('IncidentComment', backref='action', lazy='selectin')
    task_id = db.Column(db.Integer, db.ForeignKey('incident_task.id'))
    task = db.relationship('IncidentTask', backref='logs', lazy='selectin') ##TODO Change to actions
    subtask_id = db.Column(db.Integer, db.ForeignKey('incident_sub_task.id'))
    subtask = db.relationship('IncidentSubTask', backref='logs', lazy='selectin') ##TODO Change to actions
    target_users = db.relationship('User', secondary=incidentlog_target_users_junction, lazy='selectin', backref='incident_log_target')
    action_type = db.Column(db.Integer())
    reason = db.Column(db.String(256))
    extra = db.Column(db.String())
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        target_users = None
        if self.target_users:
            if len(self.target_users) > 1:
                target_users = list_of_names(self.target_users)
            else:
                target_users = self.target_users[0]
        msg = Template(self.action_strings[self.action_type]).substitute(target_users=target_users, task=self.task,
                                                                         extra=self.extra)
        return f'{msg}.'


class TaskLog(db.Model):
    action_values = {'create_subtask': 1, 'complete_subtask': 2, 'delete_subtask': 3, 'changed_description': 4,
                     'assigned_user': 5, 'removed_user': 6, 'incomplete_subtask': 7, 'add_comment': 8, 'edit_subtask': 9, 'changed_tags': 10, 'edit_task_comment': 11, 'delete_task_comment': 12}  ##TODO RE-ORDER ONCE DONE
    action_strings = {1: 'created $subtask', 2: 'marked $subtask as complete',
                      3: 'deleted $extra',
                      4: 'changed task description to "$extra"', 5: 'added $target_users to task',
                      6: 'removed $target_users from task', 7: 'marked $subtask as incomplete', 8: 'added comment to task', 9: 'edited subtask $subtask', 10: 'changed the task\'s tags', 11: 'edited task comment', 12: 'deleted task comment'}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='task_actions')
    task_id = db.Column(db.Integer, db.ForeignKey('incident_task.id'))
    task = db.relationship('IncidentTask', backref='task_logs', lazy='selectin')
    subtask_id = db.Column(db.Integer, db.ForeignKey('incident_sub_task.id'))
    subtask = db.relationship('IncidentSubTask', backref='task_logs', lazy='selectin')
    target_users = db.relationship('User', secondary=tasklog_target_users_junction, backref='task_log_target')
    action_type = db.Column(db.Integer())
    reason = db.Column(db.String(256))
    extra = db.Column(db.String())
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        target_users = None
        if self.target_users:
            if len(self.target_users) > 1:
                target_users = list_of_names(self.target_users)
            else:
                target_users = self.target_users[0]
        msg = Template(self.action_strings[self.action_type]).substitute(target_users=target_users, task=self.task,
                                                                         subtask=self.subtask,
                                                                         extra=self.extra)
        return f'{msg}.'


class RevokedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


admin = Admin(app, name='DGVOST', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Group, db.session))
admin.add_view(ModelView(Deployment, db.session))
admin.add_view(ModelView(Incident, db.session))
admin.add_view(ModelView(IncidentTask, db.session))
admin.add_view(ModelView(IncidentSubTask, db.session))
admin.add_view(ModelView(TaskComment, db.session))
admin.add_view(ModelView(IncidentComment, db.session))
admin.add_view(ModelView(IncidentMedia, db.session))
admin.add_view(ModelView(SupervisorActions, db.session))
admin.add_view(ModelView(EmailLink, db.session))
admin.add_view(ModelView(AuditLog, db.session))
admin.add_view(ModelView(IncidentLog, db.session))
admin.add_view(ModelView(TaskLog, db.session))
admin.add_view(ModelView(RevokedToken, db.session))