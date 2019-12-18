import functools
from sqlalchemy import func
from itertools import groupby
from app import app, db, socketio
from app.utils.delete import delete_subtask
from flask_socketio import emit, join_room, disconnect
from flask import render_template, redirect, url_for, request
from app.forms import LoginForm, CreateUser, CreateGroup, SetPassword
from flask_login import current_user, login_user, logout_user, login_required
from app.utils.supervisor import request_incident_complete, mark_request_complete, flag_to_supervisor
from app.models import User, Group, Deployment, Incident, IncidentTask, IncidentSubTask, SupervisorActions, EmailLink, AuditLog
from app.utils.create import create_user, create_group, create_deployment, create_incident, create_task, create_subtask, create_task_comment, create_comment
from app.utils.change import change_incident_status, change_allocation, change_public, change_incident_priority, change_task_status, change_task_description, change_task_assigned, change_subtask_status


def login_required_sockets(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
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

@app.errorhandler(404)
@login_required
def page_not_found(e):
    if current_user.is_authenticated:
        return render_template('404.html', nosidebar=True), 404
    return redirect(url_for('login'))


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('view_deployments'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(func.lower(User.email) == func.lower(form.email.data)).first()
        if user is None or not user.check_password(form.password.data):
            return render_template('login.html', title='Sign In', form=form, invalid=True)
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('view_deployments'))
    return render_template('login.html', title='Sign In', form=form, invalid=False)


@app.route('/supervisor/create_user/', methods=['GET', 'POST'])
#@login_required
def new_user():
    groups_list = [(i.id, i.name) for i in Group.query.all()]
    form = CreateUser()
    form.group.choices = groups_list
    if form.validate_on_submit():
        group = None
        if form.group.data:
            group = Group.query.get(form.group.data)
        user = create_user(form.firstname.data, form.surname.data, form.email.data, group.id if group else None, current_user)
        user.set_password('password')
        db.session.commit()
        form = CreateUser()
        form.group.choices = groups_list
    return render_template('group.html', title=' User', form=form)


@app.route('/verify/<link>/', methods=['GET', 'POST'])
@login_required
def verify_user(link):
    email = EmailLink.query.filter_by(link=link).first()
    if not email:
        return "Invalid Link"
    form = SetPassword()
    if form.validate_on_submit():
        email.user.set_password(form.password.data)
        action = AuditLog(user=email.user, action_type=AuditLog.action_values["verify_user"])
        db.session.add(action)
        db.session.delete(email)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('base.html', title='Set Password', form=form, username=email.user.username)


@app.route('/supervisor/create_group/', methods=['GET', 'POST'])
#@login_required
def new_group():
    form = CreateGroup()
    if form.validate_on_submit():
        permissions = {"view_all_incidents": form.view_all_incidents.data, "change_status": form.change_status.data,
                       "change_allocations": form.change_allocations.data, "mark_as_public": form.mark_as_public.data,
                       "new_reports": form.new_reports.data, "create_deployments": form.create_deployments.data,
                       "decision_making_log": form.decision_making_log.data, "supervisor": form.supervisor.data}
        chosen_permissions = [k for k, v in permissions.items() if v]
        create_group(form.name.data, chosen_permissions, current_user)
        form = CreateGroup()
    return render_template('group.html', title='Group', form=form)


@app.route('/')
@app.route('/deployments/', methods=['GET'])
@login_required
def view_deployments():
    groups = []
    for k, g in groupby(User.query.all(), key=lambda item: item.group):
        groups.append([[k.id, k.name], list(g)])
    return render_template('deployments.html', title='Deployments', nosidebar=True, groups=groups, back_url=url_for('view_deployments'), deployments=current_user.get_deployments())


@app.route('/deployments/<deployment_name>-<int:deployment_id>/', methods=['GET'])
@app.route('/deployments/<deployment_name>-<int:deployment_id>/incidents/', methods=['GET'])
@login_required
def view_incidents(deployment_name, deployment_id):
    deployment = Deployment.query.filter_by(id=deployment_id).first()
    if not deployment or not deployment.name_check(deployment_name):
        return render_template('404.html', nosidebar=True), 404
    incidents_stat = deployment.calculate_incidents_stat()
    return render_template('incidents.html', title=f'{deployment.name}', deployment=deployment,
                           incidents_active=True, incidents_stat=incidents_stat, incidents=current_user.get_incidents(deployment.id), back_url=url_for('view_deployments'))


@app.route('/deployments/<deployment_name>-<deployment_id>/assigned_incidents/', methods=['GET'])
@login_required
def view_assigned_incidents(deployment_name, deployment_id):
    deployment = Deployment.query.filter_by(id=deployment_id).first()
    if not deployment or not deployment.name_check(deployment_name):
        return render_template('404.html', nosidebar=True), 404
    incidents_stat = deployment.calculate_incidents_stat(current_user)
    return render_template('incidents.html', title=f'{deployment.name}', deployment=deployment,
                           assigned_incidents_active=True, incidents_stat=incidents_stat, incidents=current_user.get_incidents(deployment.id, ignore_permissions=True), back_url=url_for('view_deployments'))


@app.route('/deployments/<deployment_name>-<deployment_id>/incidents/<incident_name>-<int:incident_id>/', methods=['GET', 'POST'])
@login_required
def view_incident(deployment_name, deployment_id, incident_name, incident_id):
    incident = Incident.query.filter_by(id=incident_id, deployment_id=deployment_id).first()
    if not incident or not incident.name_check(deployment_name, incident_name):
        return render_template('404.html', nosidebar=True), 404
    if not current_user.has_permission('view_all_incidents'):
        return redirect(url_for('view_assigned_incidents', deployment_name=Incident.deployment.urlstring, deployment_id=Incident.deployment_id))
    groups = []
    for k, g in groupby(User.query.all(), key=lambda item: item.group):
        groups.append([k.name, list(g)])
    return render_template('incident.html', incident=incident, deployment=incident.deployment, groups=groups, back_url=url_for('view_incidents', deployment_name=incident.deployment.name, deployment_id=incident.deployment_id), title=f'{incident.deployment.id} - Incident {incident_id}')


@app.route('/notifications/', methods=['GET'])
@login_required
def view_notifications():
    pass


@app.route('/deployments/<deployment_name>-<deployment_id>/map/', methods=['GET'])
@login_required
def view_map(deployment_name, deployment_id):
    deployment = Deployment.query.filter_by(id=deployment_id).first()
    if not deployment or not deployment.name_check(deployment_name):
        return render_template('404.html', nosidebar=True), 404
    return render_template('map.html', title=f'{deployment}', deployment=deployment, geojson=list(filter(None, [m.generate_geojson() for m in current_user.get_incidents(deployment)])), map_active=True, back_url=url_for('view_incidents', deployment_name=deployment.name, deployment_id=deployment.id))


@app.route('/deployments/<deployment_name>-<deployment_id>/live-feed/', methods=['GET'])
@login_required
def view_live_feed(deployment_name):
    pass


@app.route('/deployments/<deployment_name>-<deployment_id>/decision-making-log/', methods=['GET'])
@login_required
def view_decision_making_log(deployment_name):
    pass


@app.route('/deployments/<deployment_name>-<deployment_id>/supervisor/actions', methods=['GET'])
@login_required
def supervisor_actions(deployment_name, deployment_id):
    deployment = Deployment.query.filter_by(id=deployment_id).first()
    if not deployment or not deployment.name_check(deployment_name):
        return render_template('404.html', nosidebar=True), 404
    actions = SupervisorActions.query.filter_by(deployment_id=deployment_id, completed=False).all()
    return render_template('actions.html', title=f'{deployment}', deployment=deployment, actions=actions, supervisor_actions_active=True, back_url=url_for('view_incidents', deployment_name=deployment.name, deployment_id=deployment.id))


@socketio.on('join')
@login_required_sockets
def on_join(data):
    if data['type'] == 0:
        join_room('deployments')
        print('Joined Private Room: deployments')
    if data['type'] == 1:
        if current_user.has_deployment_access(data['deployment_id']):
            if current_user.has_permission('view_all_incidents'):
                join_room(f'{data["deployment_id"]}-all')
                if current_user.has_permission('supervisor'):
                    join_room(f'{data["deployment_id"]}-actions-count')
                    print(f'{data["deployment_id"]}-actions-count')
                print(f'Joined Global Room: {data["deployment_id"]}-all')
            else:
                join_room(f'{data["deployment_id"]}-private')
                if current_user.has_permission('supervisor'):
                    join_room(f'{data["deployment_id"]}-actions-count')
                    print(f'{data["deployment_id"]}-actions-count')
                print(f'Joined Private Room: {data["deployment_id"]}-private')
        else:
            disconnect()
            print(f'Kicked from Room: {data["deployment_id"]}')
    elif data['type'] == 2:
        if current_user.has_incident_access(data['deployment_id'], data['incident_id']):
            join_room(f'{data["deployment_id"]}-{data["incident_id"]}')
            print(f'Joined Room: {data["deployment_id"]}-{data["incident_id"]}')
            if current_user.has_permission('supervisor'):
                join_room(f'{data["deployment_id"]}-actions-count')
                print(f'{data["deployment_id"]}-actions-count')
        else:
            disconnect()
            print(f'Kicked from Room: {data["deployment_id"]}-{data["incident_id"]}')
    elif data['type'] == 3:
        if current_user.has_permission('supervisor'):
            join_room(f'{data["deployment_id"]}-actions')
            print(f'Joined Room: {data["deployment_id"]}-actions')
        else:
            disconnect()
            print(f'Kicked from Room: {data["deployment_id"]}-actions')
    elif data['type'] == 4:
        join_room(f'{data["incident_id"]}-{data["task_id"]}')
        print(f'Joined Room: {data["incident_id"]}-{data["task_id"]}')


@socketio.on('unconnect')
@login_required_sockets
def on_unconnect(data):
    if data['type'] == 4:
        disconnect(f'{data["incident_id"]}-{data["task_id"]}')
        print(f'Kicked from Room: {data["incident_id"]}-{data["task_id"]}')


@socketio.on('create_deployment')
@login_required_sockets
#@has_permission_sockets
def create_deployment_socket(data):
    print(data)
    try:
        name = data['name']
        description = data['description']
        groups = data['groups']
        users = data['users']
    except:
        return emit('create_incident', {'message': 'Incorrect data supplied.', 'code': 403})
    create_deployment(name, description, groups, users, current_user)


@socketio.on('create_incident')
@login_required_sockets
#@has_permission_sockets
def create_incident_socket(data):
    print(data)
    try:
        name = data['name']
        description = data['description']
        incident_type = data['type']
        location = data['location']
        longitude = data['geometry'][0]
        latitude = data['geometry'][1]
        reported_via = data['reported_via']
        reference = data['reference']
    except: ##TODO Less vague exception handling
        return emit('create_incident', {'message': 'Incorrect data supplied.', 'code': 403})
    if incident_type not in Incident.incident_types.keys():
        return emit('create_incident', {'message': 'Incorrect data supplied.', 'code': 403})
    deployment = Deployment.query.filter_by(id=data['deployment_id']).first()
    if not deployment:
        return emit('create_incident', {'message': 'Unable to find the deployment.', 'code': 404})
    incident = create_incident(name, description, incident_type, location, longitude, latitude, reported_via, reference, deployment, current_user)
    if current_user.has_permission('supervisor'):
        emit('redirect_incident', {'url': url_for('view_incident', deployment_name=deployment.name, deployment_id=deployment.id, incident_name=incident.name, incident_id=incident.id), 'code': 200})


@socketio.on('create_incident_task')
@login_required_sockets
#@has_permission_sockets
def create_incident_task_socket(data):
    print(data)
    try: ##TODO Add in incident id and deployment id in here too
        name = data['name']
        users = data['users']
        description = data['description']
    except:
        return emit('create_incident_task', {'message': 'Incorrect data supplied.', 'code': 403})
    incident = Incident.query.filter(Deployment.id == data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('create_incident_task', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    if users:
        users = User.query.filter(User.id.in_(data['users'])).all()
        if set(users) - set(incident.assigned_to):
            change_allocation(incident, users, current_user)
    create_task(name, users, description, incident, current_user)


@socketio.on('create_incident_subtask')
@login_required_sockets
#@has_permission_sockets
def create_incident_subtask_socket(data):
    print(data)
    try: ##TODO Add in incident id and deployment id in here too
        name = data['name']
        task_id = data['task_id']
        users = data['users']
    except:
        return emit('create_incident_subtask', {'message': 'Incorrect data supplied.', 'code': 403})
    task = IncidentTask.query.filter_by(incident_id=data['incident_id'], id=task_id).first()
    if not task or task.incident.id != data['incident_id'] or task.incident.deployment_id != data['deployment_id']:
        return emit('create_incident_subtask', {'message': 'Unable to find the deployment, incident or task.', 'code': 404})
    if users:
        users = User.query.filter(User.id.in_(data['users'])).all()
        if any([m for m in users if m not in task.incident.assigned_to]):
            change_allocation(task.incident, users + task.incident.assigned_to, current_user)
        print(task.assigned_to)
        if any([m for m in users if m not in task.assigned_to]):
            change_task_assigned(task, users + task.assigned_to, current_user)
        print(task.assigned_to)
    create_subtask(name, users, task, current_user)


@socketio.on('create_task_comment')
@login_required_sockets
#@has_permission_sockets
def create_task_comment_socket(data):
    try:
        text = data['text']
    except:
        return emit('create_incident_comment', {'message': 'Incorrect data supplied.', 'code': 403})
    task = IncidentTask.query.filter_by(incident_id=data['incident_id'], id=data['task_id']).first()
    if not task or task.incident.id != data['incident_id'] or task.incident.deployment_id != data['deployment_id']:
        return emit('create_incident_subtask', {'message': 'Unable to find the deployment, incident or task.', 'code': 404})
    create_task_comment(text, task, current_user)


@socketio.on('create_incident_comment')
@login_required_sockets
#@has_permission_sockets
def create_incident_comment_socket(data):
    try:
        text = data['text']
    except:
        return emit('create_incident_comment', {'message': 'Incorrect data supplied.', 'code': 403})
    incident = Incident.query.filter(Deployment.id == data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('create_incident_comment', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    create_comment(text, incident, current_user)


@socketio.on('change_incident_status')
@login_required_sockets
#@has_permission_sockets
def change_incident_status_socket(data):
    print(data)
    try: ##TODO Make sure not None
        status = data['status']
    except:
        return emit('change_incident_status', {'message': 'Incorrect data supplied.', 'code': 403})
    incident = Incident.query.filter(Deployment.id==data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('change_incident_status', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    if change_incident_status(incident, status, current_user) is False:
        return emit('change_incident_status', {'message': 'Incident already has this status.', 'code': 400})


@socketio.on('change_incident_allocation')
@login_required_sockets
#@has_permission_sockets
def change_incident_allocation_socket(data):
    #if not current_user.has_permission('change_allocation'):
    #    return jsonify(data='You don\'t have permission to change an incident\'s allocation.'), 403
    print(data)
    incident = Incident.query.filter(Deployment.id==data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('change_incident_allocation', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    users = [n for n in [User.query.filter_by(id=int(m)).first() for m in data['users'] if m] if n and n.has_deployment_access(incident.deployment)]
    if change_allocation(incident, users, current_user) is False:
        return emit('change_incident_allocation', {'message': 'Didn\'t change assigned users.', 'code': 400})


@socketio.on('change_public')
@login_required_sockets
#@has_permission_sockets
def change_public_socket(data):
    print(data)
    try: ##TODO Add in function to get data
        public = data['public']
    except:
        return emit('change_public', {'message': 'Incorrect data supplied.', 'code': 403})
    incident = Incident.query.filter(Deployment.id == data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('change_incident_priority', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    if change_public(incident, public, current_user) is False:
        return emit('change_public', {'message': 'Incident already has this priority.', 'code': 400})


@socketio.on('change_incident_priority')
@login_required_sockets
#@has_permission_sockets
def change_incident_priority_socket(data):
    print(data)
    #if not current_user.has_permission('change_priority'):
    #    return jsonify(data='You don\'t have permission to change an incident\'s priority.'), 403
    try: ##TODO Add in function to get data
        priority = data['priority']
    except:
        return emit('change_incident_priority', {'message': 'Incorrect data supplied.', 'code': 403})
    if priority not in ['Standard', 'Prompt', 'Immediate']:
        return emit('change_incident_priority', {'message': 'Incorrect data supplied.', 'code': 403})
    incident = Incident.query.filter(Deployment.id == data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('change_incident_priority', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    if change_incident_priority(incident, priority, current_user) is False:
        return emit('change_incident_priority', {'message': 'Incident already has this priority.', 'code': 400})


@socketio.on('change_task_status')
@login_required_sockets
#@has_permission_sockets
def change_task_status_socket(data):
    print(data)
    task_id = data['task_id']
    completed = data['completed']
       # return emit('change_task_status', {'message': 'Incorrect data supplied.', 'code': 403})
    task = IncidentTask.query.filter_by(incident_id=data['incident_id'], id=task_id).first()
    if not task or task.incident.deployment_id != data['deployment_id']:
        return emit('change_task_status', {'message': 'Unable to find the deployment, incident or task.', 'code': 404})
    if change_task_status(task, completed, current_user) is False:
        return emit('change_task_status', {'message': 'Task already has this status.', 'code': 400})


@socketio.on('change_task_description')
@login_required_sockets
#@has_permission_sockets
def change_task_description_socket(data):
    print(data)
    task_id = data['task_id']
    description = data['description']
       # return emit('change_task_status', {'message': 'Incorrect data supplied.', 'code': 403})
    task = IncidentTask.query.filter_by(incident_id=data['incident_id'], id=task_id).first()
    if not task or task.incident.deployment_id != data['deployment_id']:
        return emit('change_task_status', {'message': 'Unable to find the deployment, incident or task.', 'code': 404})
    if change_task_description(task, description, current_user) is False:
        return emit('change_task_status', {'message': 'Task already has this status.', 'code': 400})


@socketio.on('change_task_assigned')
@login_required_sockets
#@has_permission_sockets
def change_task_assigned_socket(data):
    print(data)
    try: ##TODO Add in incident id and deployment id in here too
        task_id = data['task_id']
        users = data['users']
    except:
        return emit('change_task_assigned', {'message': 'Incorrect data supplied.', 'code': 403})
    task = IncidentTask.query.filter_by(incident_id=data['incident_id'], id=task_id).first()
    if not task or task.incident.id != data['incident_id'] or task.incident.deployment_id != data['deployment_id']:
        return emit('change_task_assigned', {'message': 'Unable to find the deployment, incident or task.', 'code': 404})
    if users:
        users = User.query.filter(User.id.in_(data['users'])).all()
        if any([m for m in users if m not in task.incident.assigned_to]):
            change_allocation(task.incident, users + task.incident.assigned_to, current_user)
        if any([m for m in users if m not in task.assigned_to]):
            change_task_assigned(task, users + task.assigned_to, current_user)


@socketio.on('change_subtask_status')
@login_required_sockets
#@has_permission_sockets
def change_subtask_status_socket(data):
    print(data)
    subtask_id = data['subtask_id']
    completed = data['completed']
       # return emit('change_task_status', {'message': 'Incorrect data supplied.', 'code': 403})
    subtask = IncidentSubTask.query.filter_by(task_id=data['task_id'], id=subtask_id).first()
    if not subtask or subtask.task.incident.id != data['incident_id'] or subtask.task.incident.deployment_id != data['deployment_id']:
        return emit('change_subtask_status', {'message': 'Unable to find the deployment, incident or task.', 'code': 404})
    if change_subtask_status(subtask, completed, current_user) is False:
        return emit('change_subtask_status', {'message': 'Task already has this status.', 'code': 400})


@socketio.on('view_task')
@login_required_sockets
#@has_permission_sockets
def view_task_socket(data):
    print(data)
    task_id = data['task_id']
    task = IncidentTask.query.filter_by(incident_id=data['incident_id'], id=task_id).first()
    if not task or task.incident.deployment_id != data['deployment_id']:
        return emit('view_task', {'message': 'Unable to find the deployment, incident or task.', 'code': 404})
    return emit('view_task', {'id': task.id, 'name': task.name, 'description': task.description, 'subtasks': task.get_subtasks(), 'comments': task.get_comments(), 'actions': task.get_actions(), 'chosen_ids': list([m.id for m in task.assigned_to]), 'code': 200})


@socketio.on('delete_subtask')
@login_required_sockets
#@has_permission_sockets
def delete_subtask_socket(data):
    print(data)
    subtask_id = data['subtask_id']
       # return emit('change_task_status', {'message': 'Incorrect data supplied.', 'code': 403})
    subtask = IncidentSubTask.query.filter_by(task_id=data['task_id'], id=subtask_id).first()
    if not subtask or subtask.task.incident.id != data['incident_id'] or subtask.task.incident.deployment_id != data['deployment_id']:
        return emit('delete_subtask', {'message': 'Unable to find the deployment, incident or task.', 'code': 404})
    delete_subtask(subtask, current_user)


@socketio.on('request_incident_complete')
@login_required_sockets
#@has_permission_sockets
def request_incident_complete_socket(data):
    print(data)
    try: ##TODO Make sure not None
        status = data['status']
        reason = data['reason']
    except:
        return emit('request_incident_complete', {'message': 'Incorrect data supplied.', 'code': 403})
    incident = Incident.query.filter(Deployment.id==data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('request_incident_complete', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    if request_incident_complete(incident, status, reason, current_user) is False:
        return emit('request_incident_complete', {'message': 'Incident already has this status.', 'code': 400})


@socketio.on('flag_to_supervisor')
@login_required_sockets
#@has_permission_sockets
def flag_to_supervisor_socket(data):
    print(data)
    try: ##TODO Make sure not None
        reason = data['reason']
    except:
        return emit('flag_to_supervisor', {'message': 'Incorrect data supplied.', 'code': 403})
    incident = Incident.query.filter(Deployment.id==data['deployment_id'], Incident.id == data['incident_id']).first()
    if not incident:
        return emit('flag_to_supervisor', {'message': 'Unable to find the deployment or incident.', 'code': 404})
    if flag_to_supervisor(incident, reason, current_user) is False:
        return emit('flag_to_supervisor', {'message': 'Incident already has this status.', 'code': 400})


@socketio.on('mark_request_complete')
@login_required_sockets
#@has_permission_sockets
def mark_request_complete_socket(data):
    print(data)
       # return emit('change_task_status', {'message': 'Incorrect data supplied.', 'code': 403})
    requested_action = SupervisorActions.query.filter_by(id=data['id'], deployment_id=data['deployment_id']).first()
    if not requested_action:
        return emit('mark_request_complete', {'message': 'Unable to find the deployment or action requested item.', 'code': 404})
    mark_request_complete(requested_action, current_user)