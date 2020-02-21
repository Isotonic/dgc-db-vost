import functools
from .models import User
from jwt import exceptions
from app import db, socketio
from flask_login import current_user, login_user
from flask_jwt_extended import decode_token
from flask_socketio import emit, join_room, disconnect


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


@socketio.on('join')
def on_join(data):
    try:
        token = decode_token(data['accessToken'])
    except (exceptions.ExpiredSignatureError, KeyError):
        return
    user = User.query.filter_by(id=token['identity'], status=1).first()
    if not user:
        return
    login_user(user)
    join_room(f'{current_user.id}')
    join_room('deployments')
    handle_join_deployment(user, data)
    print(f'Connected {user}')
    emit('CONNECTED', {'code': 200})


@socketio.on('leave')
@login_required_sockets
def on_leave(data):
    try:
        deploymentId = data['deploymentId']
    except KeyError:
        return
    if current_user.has_permission('view_all_incidents'):
        disconnect(f'{deploymentId}-all')
    else:
        disconnect(f'{deploymentId}-{current_user.id}')


@socketio.on('join_deployment')
@login_required_sockets
def on_join_deployment(data):
    handle_join_deployment(current_user, data)


@socketio.on('join_admin')
@login_required_sockets
def on_join_admin():
    if current_user.has_permission('supervisor'):
        print('Joined admin')
        join_room('admin')
