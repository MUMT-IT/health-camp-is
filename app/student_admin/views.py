import random

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db, superuser
from app.services.models import User, ClientAddress, Organism, Client, StoolTestRecord
from app.student_admin import admin_bp as admin
from app.student_admin.forms import AddressForm, OrganismForm, ClientUploadForm
import pandas as pd


@admin.route('/projects/<int:project_id>')
@superuser
@login_required
def index(project_id):
    return render_template('student_admin/index.html', project_id=project_id)


@admin.route('/projects/<int:project_id>/users')
@superuser
@login_required
def list_users(project_id):
    users = User.query.filter_by(is_approved=False)
    return render_template('student_admin/users.html', users=users, project_id=project_id)


@admin.route('/projects/<int:project_id>/users/<int:user_id>/approve')
@superuser
@login_required
def approve_user(user_id, project_id):
    u = User.query.get(user_id)
    if u:
        u.is_approved = True
        db.session.add(u)
        db.session.commit()
        flash('The user has been approved', 'success')
        return redirect(url_for('student_admin.list_users', project_id=project_id))


@admin.route('/addresses/add', methods=['GET', 'POST'])
@admin.route('/addresses/<int:addr_id>/edit', methods=['GET', 'POST'])
@superuser
@login_required
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


@admin.route('/organisms/add', methods=['GET', 'POST'])
@admin.route('/organisms/<int:org_id>/edit', methods=['GET', 'POST'])
@superuser
@login_required
def edit_organism(org_id=None):
    organisms = Organism.query.all()
    if org_id:
        org = Organism.query.get(org_id)
        form = OrganismForm(obj=org)
    else:
        form = OrganismForm()

    if form.validate_on_submit():
        if org_id:
            form.populate_obj(org)
            flash('The organism has been updated.', 'success')
            db.session.add(org)
        else:
            new_org = ClientAddress()
            form.populate_obj(new_org)
            flash('New organism has been added.', 'success')
            db.session.add(new_org)
        db.session.commit()
    return render_template('student_admin/organism_form.html',
                           form=form, organisms=organisms, org_id=org_id)


@admin.route('/projects<int:project_id>/clients/upload', methods=['GET', 'POST'])
@superuser
@login_required
def upload_clients(project_id):
    form = ClientUploadForm()
    if form.validate_on_submit():
        f = form.upload.data
        df = pd.read_excel(f)
        for idx, row in df.iterrows():
            client = Client(
                firstname=row['firstname'],
                lastname=row['lastname'],
                project_id=project_id,
                updated_by=current_user,
            )
            if form.use_lab_number_as_client_number.data:
                client.client_number = row['labno']
            if form.random_pid.data:
                client.pid = 'fake' + ''.join([str(random.randint(0, 9)) for i in range(9)])
            if row.get('address'):
                address = ClientAddress.query.filter_by(name=row.get('address')).first()
                client.address = address
            db.session.add(client)
            if row.get('stool'):
                if row.get('stool') is True:
                    record = StoolTestRecord(
                        client=client,
                        method=row.get('stool_method'),
                        lab_number=row.get('labno')
                    )
                    db.session.add(record)
        db.session.commit()
    else:
        for field, errors in form.errors.items():
            flash(f'{field} : {errors}', 'danger')
    return render_template('student_admin/upload_clients.html', form=form)
