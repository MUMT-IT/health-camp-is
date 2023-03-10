from flask import render_template, redirect, url_for, flash, request

from app import db
from app.services import service_bp as services
from app.services.forms import ClientForm, ClientPhysicalProfileForm, TestForm, TestRecordForm
from app.services.models import Client, ClientPhysicalProfile, Test, TestRecord


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


@services.route('/clients')
def list_clients():
    clients = Client.query.all()
    return render_template('services/clients/list.html', clients=clients)


@services.route('/clients/physical-exam')
def physical_exam_profile_main():
    client_number = request.args.get('client_number')
    if client_number:
        client = Client.query.filter_by(client_number=client_number).first()
        if client:
            return redirect(url_for('services.add_physical_exam_profile', client_id=client.id))
    return render_template('services/clients/physical_exam_profile_main.html')


@services.route('/clients/<int:client_id>/physical-exam', methods=['GET', 'POST'])
def add_physical_exam_profile(client_id):
    client = Client.query.get(client_id)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('services.physical_exam_profile'))

    form = ClientPhysicalProfileForm()
    if form.validate_on_submit():
        pp = ClientPhysicalProfile()
        form.populate_obj(pp)
        pp.client = client
        db.session.add(pp)
        db.session.commit()
        flash('New data have been saved.', 'success')
        return redirect(url_for('services.physical_exam_profile_main'))
    return render_template('services/clients/physical_exam_form.html', form=form, client=client)


@services.route('/clients/physical-exam/<int:rec_id>/edit', methods=['GET', 'POST'])
def edit_physical_exam_profile(rec_id):
    rec = ClientPhysicalProfile.query.get(rec_id)
    form = ClientPhysicalProfileForm(obj=rec)
    if form.validate_on_submit():
        form.populate_obj(rec)
        db.session.add(rec)
        db.session.commit()
        flash('Data have been updated.', 'success')
        return redirect(url_for('services.add_physical_exam_profile',
                                client_id=rec.client.id))
    return render_template('services/clients/physical_exam_form.html', form=form)


@services.route('/clients/<int:client_id>/profile')
def client_profile(client_id):
    client = Client.query.get(client_id)
    return render_template('services/clients/profile.html', client=client)


@services.route('/tests')
def list_tests():
    tests = Test.query.all()
    return render_template('services/tests/list.html', tests=tests)


@services.route('/tests/register', methods=['POST', 'GET'])
def register_test():
    form = TestForm()
    if form.validate_on_submit():
        test = Test()
        form.populate_obj(test)
        db.session.add(test)
        db.session.commit()
        flash('New test has been added.', 'success')
        return redirect(url_for('services.list_tests'))
    return render_template('services/tests/register.html', form=form)


@services.route('/tests/<int:test_id>/edit', methods=['POST', 'GET'])
def edit_test(test_id):
    test = Test.query.get(test_id)
    form = TestForm(obj=test)
    if form.validate_on_submit():
        form.populate_obj(test)
        db.session.add(test)
        db.session.commit()
        flash('Test has been updated.', 'success')
        return redirect(url_for('services.list_tests'))
    return render_template('services/tests/register.html', form=form)


@services.route('/tests/<int:test_id>/records')
def test_record_main(test_id):
    client_number = request.args.get('client_number')
    client = Client.query.filter_by(client_number=client_number).first()
    if client:
        return redirect(url_for('services.add_test_record', test_id=test_id, client_id=client.id))
    flash('Client number not found', 'danger')
    return render_template('services/tests/main.html')


@services.route('/clients/<int:client_id>/tests/<int:test_id>/records/add',
                methods=['GET', 'POST'])
def add_test_record(test_id, client_id):
    client = Client.query.get(client_id)
    test = Test.query.get(test_id)
    form = TestRecordForm()
    if form.validate_on_submit():
        rec = TestRecord()
        form.populate_obj(rec)
        rec.test = test
        rec.client_id = client_id
        db.session.add(rec)
        db.session.commit()
        flash('Test has been updated.', 'success')
        return redirect(url_for('services.test_record_main', test_id=test_id))
    return render_template('services/tests/record_form.html', form=form, test=test, client=client)
