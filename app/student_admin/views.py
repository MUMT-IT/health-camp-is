from flask import render_template, flash, redirect, url_for

from app import db
from app.services.models import User, ClientAddress
from app.student_admin import admin_bp as admin
from app.student_admin.forms import AddressForm


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


@admin.route('/addresses/add', methods=['GET', 'POST'])
@admin.route('/addresses/<int:addr_id>/edit', methods=['GET', 'POST'])
def edit_address(addr_id=None):
    addresses = ClientAddress.query.all()
    if addr_id:
        addr = ClientAddress.query.get(addr_id)
        form = AddressForm(obj=addr)
    else:
        form = AddressForm()

    if form.validate_on_submit():
        if addr_id:
            form.populate_obj(addr)
            flash('The address has been updated.', 'success')
            db.session.add(addr)
        else:
            new_addr = ClientAddress()
            form.populate_obj(new_addr)
            flash('New addresss has been added.', 'success')
            db.session.add(new_addr)
        db.session.commit()
    return render_template('student_admin/address_form.html',
                           form=form, addresses=addresses, addr_id=addr_id)
