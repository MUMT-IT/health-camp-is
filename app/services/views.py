from flask import render_template, redirect, url_for, flash

from app import db
from app.services import service_bp as services
from app.services.forms import ClientForm
from app.services.models import Client


@services.route('/')
def index():
    return render_template('services/index.html')


@services.route('/clients/registration', methods=['GET', 'POST'])
def register_client():
    form = ClientForm()
    if form.validate_on_submit():
        client = Client()
        form.populate_obj(client)
        db.session.add(client)
        db.session.commit()
        flash('New client has been added.', 'success')
        return redirect(url_for('services.index'))
    return render_template('services/clients/registration.html', form=form)
