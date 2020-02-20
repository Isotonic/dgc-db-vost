import functools
from .models import User
from app import app, db, socketio
from flask_jwt_extended import decode_token
from flask_login import current_user, login_user
from flask_socketio import emit, join_room, disconnect


def login_required_sockets(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return emit('login', {'message': 'Not logged in.', 'code': 401})
        else:
            return f(*args, **kwargs)
    return wrapped

def has_permission_sockets(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.has_permission(None):
            return emit('change_status', {'message': 'You don\'t have permission to change an incident\'s status.', 'code': 403})
        else:
            return f(*args, **kwargs)
    return wrapped

def handle_join(data):
    print(data)
    join_room(f'{current_user.id}')
    join_room('deployments')
    if 'deploymentId' not in data.keys():
        return
    if current_user.has_deployment_access(data['deploymentId']):
        if current_user.has_permission('supervisor'):
            print('Supervisor')
            join_room(f'{data["deploymentId"]}-all')
            join_room(f'{data["deploymentId"]}-supervisor')
        if current_user.has_permission('view_all_incidents'):
            join_room(f'{data["deploymentId"]}-all')
        else:
            join_room(f'{data["deploymentId"]}-limited')

@socketio.on('login')
def on_login(data):
    if 'accessToken' not in data.keys():
        return
    token = decode_token(data['accessToken'])
    user = User.query.filter_by(id=token['identity'], status=1).first()
    if not user:
        return
    login_user(user)
    handle_join(data)

@socketio.on('join')
@login_required_sockets
def on_join(data):
    handle_join(data)

@socketio.on('unconnect')
@login_required_sockets
def on_unconnect(data):
    if data['type'] == 4:
        disconnect(f'{data["incident_id"]}-{data["task_id"]}')
        print(f'Kicked from Room: {data["incident_id"]}-{data["task_id"]}')
