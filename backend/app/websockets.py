import functools
from jwt import exceptions
from app import db, socketio
from datetime import datetime
from flask_restx import marshal
from .models import User, Incident
from flask_jwt_extended import decode_token
from .api.utils.models import incident_model
from flask_login import current_user, login_user
from .api.utils.models import user_model_without_group
from flask_socketio import emit, join_room, leave_room


assigned_rooms = [] # Store connected users that are only able to see assigned incidents.
viewing_incidents = {} # Store which incidents user's are currently viewing.

def login_required_sockets(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return emit('login', {'message': 'Not logged in.', 'code': 401})
        else:
            return f(*args, **kwargs)
    return wrapped

def handle_join_deployment(user, data):
    try:
        deploymentId = data['deploymentId']
    except KeyError:
        return
    if user.has_deployment_access(deploymentId):
        if user.has_permission('supervisor'):
            join_room(f'{deploymentId}-all')
            join_room(f'{deploymentId}-supervisor')
        elif user.has_permission('view_all_incidents'):
            join_room(f'{deploymentId}-all')
        else:
            join_room(f'{deploymentId}-{user.id}')
            if f'{deploymentId}-{user.id}' not in assigned_rooms:
                assigned_rooms.append(f'{deploymentId}-{user.id}')


@socketio.on('join')
def on_join(data):
    try:
        token = decode_token(data['accessToken'])
    except (exceptions.ExpiredSignatureError, exceptions.DecodeError, KeyError):
        return
    user = User.query.filter(User.id==token['identity'], User.status>=1).first()
    if not user:
        return
    login_user(user)
    join_room(f'{current_user.id}')
    if current_user.group:
        join_room(f'{current_user.group.id}')
    join_room('all')
    join_room('deployments')
    handle_join_deployment(user, data)
    emit('CONNECTED', {'code': 200})


@socketio.on('leave')
@login_required_sockets
def on_leave(data):
    try:
        deploymentId = data['deploymentId']
    except KeyError:
        return
    if current_user.has_permission('supervisor'):
        join_room(f'{deploymentId}-supervisor')
    if current_user.has_permission('view_all_incidents'):
        leave_room(f'{deploymentId}-all')
    else:
        leave_room(f'{deploymentId}-{current_user.id}')
        if f'{deploymentId}-{current_user.id}' in assigned_rooms:
            assigned_rooms.remove(f'{deploymentId}-{current_user.id}')
            emit('ignoring_room', {'room': f'{deploymentId}-{current_user.id}'}, namespace='/', room=f'{deploymentId}-{current_user.id}', include_self=False)


@socketio.on('unignore_room')
@login_required_sockets
def on_unignore_room(data):
    try:
        room = data['room']
    except KeyError:
        return
    if room not in assigned_rooms:
        assigned_rooms.append(room)


@socketio.on('viewing_incident')
@login_required_sockets
def on_viewing_incident(data):
    try:
        incident_id = data['incidentId']
        send_changes_only = data['sendChangesOnly']
    except KeyError:
        return
    if not current_user.has_incident_access(incident_id):
        return
    if incident_id not in viewing_incidents.keys():
        viewing_incidents[incident_id] = {current_user.id: datetime.utcnow().timestamp()}
    elif incident_id in viewing_incidents.keys() and current_user.id not in viewing_incidents[incident_id]:
        viewing_incidents[incident_id][current_user.id] = datetime.utcnow().timestamp()
    else:
        changed = False
        now = datetime.utcnow().timestamp()
        viewing_incidents[incident_id][current_user.id] = now
        for x_key, x_value in viewing_incidents.items():
            for y_key, y_value in list(x_value.items()):
                if now - y_value > 120:
                    changed = True
                    del viewing_incidents[x_key][y_key]
        if not changed and send_changes_only:
            return
    join_room(f'{incident_id}-viewing')
    users_marshalled = []
    users = User.query.filter(User.id.in_(viewing_incidents[incident_id].keys())).all()
    for x in users:
        users_marshalled.append(marshal(x, user_model_without_group))
    emit('viewing_incident', {'users': users_marshalled}, namespace='/', room=f'{incident_id}-viewing')


@socketio.on('leave_viewing_incident')
@login_required_sockets
def on_leave_viewing_incident(data):
    try:
        incident_id = data['incidentId']
    except KeyError:
        return
    if incident_id in viewing_incidents.keys() and current_user.id in viewing_incidents[incident_id]:
        leave_room(f'{incident_id}-viewing')
        del viewing_incidents[incident_id][current_user.id]
        users_marshalled = []
        users = User.query.filter(User.id.in_(viewing_incidents[incident_id].keys())).all()
        for x in users:
            users_marshalled.append(marshal(x, user_model_without_group))
        emit('viewing_incident', {'users': users_marshalled}, namespace='/', room=f'{incident_id}-viewing', ignore_self=True)


@socketio.on('join_deployment')
@login_required_sockets
def on_join_deployment(data):
    handle_join_deployment(current_user, data)


@socketio.on('join_new_group')
@login_required_sockets
def on_join_new_group(data):
    try:
        oldGroupId = data['oldGroupId']
        leave_room(f'{oldGroupId}')
    except KeyError:
        pass
    if current_user.group:
        join_room(f'{current_user.group.id}')


@socketio.on('leave_supervisor')
@login_required_sockets
def on_leave_all(data):
    try:
        deploymentId = data['deploymentId']
        leave_room(f'{deploymentId}-supervisor')
    except KeyError:
        return


@socketio.on('leave_all')
@login_required_sockets
def on_leave_all(data):
    try:
        deploymentId = data['deploymentId']
        leave_room(f'{deploymentId}-all')
    except KeyError:
        return


@socketio.on('join_admin')
@login_required_sockets
def on_join_admin():
    if current_user.has_permission('supervisor'):
        join_room('admin')

