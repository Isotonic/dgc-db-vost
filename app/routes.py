from app import app, db
from app.utils.create import new_user, new_group
from app.models import User, Group, EmailLink, ActionLog
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user
from app.forms import LoginForm, CreateUser, CreateGroup, SetPassword


@app.route('/')
@app.route('/index')
def index():
    return render_template('base.html', title='Index')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/supervisor/create_user', methods=['GET', 'POST'])
def create_new_user():
    groups_list = [(i.id, i.name) for i in Group.query.all()]
    form = CreateUser()
    form.group.choices = groups_list
    if form.validate_on_submit():
        group = None
        if form.group.data:
            group = Group.query.get(form.group.data)
        email_link = new_user(form.username.data, form.email.data, group.id if group else None, current_user)
        flash('Congratulations, you are now a registered user!')
        return email_link.link
    return render_template('new_user.html', title='Create New User', form=form)


@app.route('/supervisor/create_group', methods=['GET', 'POST'])
def create_new_group():
    form = CreateGroup()
    if form.validate_on_submit():
        permissions = {"view_all_incidents": form.view_all_incidents.data, "change_status": form.change_status.data,
                       "change_allocations": form.change_allocations.data, "mark_as_public": form.mark_as_public.data,
                       "new_reports": form.new_reports.data, "create_deployments": form.create_deployments.data,
                       "decision_making_log": form.decision_making_log.data, "supervisor": form.supervisor.data}
        chosen_permissions = [k for k, v in permissions.items() if v]
        group = new_group(form.name.data, chosen_permissions, current_user)
        flash('Congratulations, you created a group!')
        return redirect(url_for('create_new_user'))
    return render_template('new_group.html', title='Create New Group', form=form)


@app.route('/verify/<link>', methods=['GET', 'POST'])
def verify_user(link):
    email = EmailLink.query.filter_by(link=link).first()
    if not email:
        return "Invalid Link"
    form = SetPassword()
    if form.validate_on_submit():
        email.user.set_password(form.password.data)
        action = ActionLog(user=email.user, action_type=ActionLog.action_values["verify_user"])
        db.session.add(action)
        db.session.delete(email)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    print(form.errors)
    return render_template('verify.html', title='Set Password', form=form, username=email.user.username)
