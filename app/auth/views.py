from flask import render_template, flash, url_for, redirect
from flask_login import login_user, current_user, logout_user

from app import db, login_manager
from app.auth import auth_bp as auth
from app.auth.forms import UserForm, LoginForm
from app.services.models import User

login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        user.set_password(form.new_password.data)
        db.session.add(user)
        db.session.commit()
        flash('The user has been registered.', 'success')
        return redirect(url_for('services.index'))
    return render_template('auth/registration.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    register_form = UserForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if user.is_authenticated:
                flash('Logged in successfully', 'success')
                return redirect(url_for('services.index'))
            else:
                flash('This account has not been approved yet. Please contact the admin.', 'warning')
                return redirect(url_for('auth.login'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html', form=form, register_form=register_form)


@auth.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have logged out.', 'success')
        return redirect(url_for('index'))
    else:
        flash('You are not logged in.', 'warning')
        return redirect(url_for('auth.login'))
