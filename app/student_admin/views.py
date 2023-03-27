from flask import render_template, flash, redirect, url_for

from app import db
from app.services.models import User
from app.student_admin import admin_bp as admin


@admin.route('/')
def index():
    return render_template('student_admin/index.html')


@admin.route('/users')
def list_users():
    users = User.query.filter_by(is_approved=False)
    return render_template('student_admin/users.html', users=users)


@admin.route('/users/<int:user_id>/approve')
def approve_user(user_id):
    u = User.query.get(user_id)
    if u:
        u.is_approved = True
        db.session.add(u)
        db.session.commit()
        flash('The user has been approved', 'success')
        return redirect(url_for('student_admin.list_users'))
