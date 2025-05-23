import random
from collections import defaultdict
from datetime import datetime
from pytz import timezone

import arrow
import gviz_api
from flask import render_template, redirect, url_for, flash, request, make_response, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db, superuser
from app.services import service_bp as services
from app.services.forms import create_client_form, ClientPhysicalProfileForm, TestForm, TestRecordForm, StoolTestForm, \
    HealthRecordForm, create_test_profile_record_form
from app.services.models import Client, ClientPhysicalProfile, Test, TestRecord, StoolTestRecord, HealthRecord, \
    Organism, Stage, StoolTestReportItem, Project, TestProfile


@services.route('/projects')
@login_required
def projects():
    projects = Project.query
    return render_template('services/projects.html', projects=projects)


@services.route('/projects/<int:project_id>')
@login_required
def index(project_id):
    return render_template('services/index.html', project_id=project_id)


@services.route('/projects/<int:project_id>/statistics')
@login_required
def show_statistics(project_id):
    return render_template('services/statistics.html', project_id=project_id)


@services.route('/projects/<int:project_id>/clients/registration', methods=['GET', 'POST'])
@login_required
def register_client(project_id):
    pid = request.args.get('pid')
    client = Client.query.filter_by(pid=pid).first()
    if client:
        flash('Existing client! Welcome back ;)', 'success')
        return redirect(url_for('services.edit_client', client_id=client.id))
    ClientForm = create_client_form(project_id)
    form = ClientForm()
    if form.validate_on_submit():
        client = Client()
        form.populate_obj(client)
        if form.use_pid_as_hn.data:
            client.client_number = client.pid
        client.project_id = project_id
        client.updated_by = current_user
        db.session.add(client)
        db.session.commit()
        flash('New client has been added.', 'success')
        return redirect(url_for('services.edit_client', client_id=client.id, project_id=project_id))
    else:
        for field in form.errors:
            flash(f'{field}: {form.errors[field]}', 'danger')
    return render_template('services/clients/registration.html', form=form, project_id=project_id)


@services.route('/projects/<int:project_id>/clients/<int:client_id>/edit', methods=['GET', 'POST', 'DELETE'])
@login_required
def edit_client(client_id, project_id):
    client = Client.query.get(client_id)
    health_form = None
    if client:
        if request.method == "DELETE":
            db.session.delete(client)
            db.session.commit()
            resp = make_response()
            resp.headers['HX-Redirect'] = url_for('services.list_clients', project_id=project_id)
            return resp

        ClientForm = create_client_form(project_id=client.project_id)
        form = ClientForm(obj=client)
        health_form = HealthRecordForm()
    else:
        flash('The client is not found.', 'danger')
    if form.validate_on_submit():
        form.populate_obj(client)
        client.updated_by = current_user
        db.session.add(client)
        db.session.commit()
        flash('Client data have been update.', 'success')
    return render_template('services/clients/registration.html',
                           project_id=project_id,
                           form=form, client=client, health_form=health_form)


@services.route('/random-pid')
@login_required
def random_pid():
    while True:
        pid = 'fake' + ''.join([str(random.randint(0, 9)) for i in range(9)])
        client = Client.query.filter_by(pid=pid).first()
        if client is None:
            break
    return f'''
      <input class="input" id="pid" name="pid" type="text" value="{pid}">
    '''


@services.route('/projects/<int:project_id>/clients')
@login_required
def list_clients(project_id):
    return render_template('services/clients/list.html', project_id=project_id)


@services.route('/api/projects/<int:project_id>/profiles/<int:profile_id>')
@login_required
def get_client_list_profile(project_id, profile_id):
    query = Client.query.filter_by(project_id=project_id)
    records_total = query.count()
    search = request.args.get('search[value]')
    query = query.filter(or_(Client.client_number.ilike('%{}%'.format(search)),
                             Client.firstname.ilike('%{}%'.format(search)),
                             Client.lastname.ilike('%{}%'.format(search)),
                             Client.pid.ilike('%{}%'.format(search)),
                             Client.address.has(name=search),
                             ),
                         )
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    total_filtered = query.count()
    query = query.offset(start).limit(length)
    data = []
    for r in query:
        d = r.to_dict()
        if profile_id:
            d['url'] = url_for('services.add_test_profile_record',
                               client_id=r.id,
                               project_id=project_id,
                               profile_id=profile_id)
        elif request.args.get('for') == 'physical-exam':
            d['url'] = url_for('services.add_physical_exam_profile',
                               client_id=r.id,
                               project_id=project_id)
        elif request.args.get('for') == 'health-record':
            d['url'] = url_for('services.add_health_record',
                               client_id=r.id,
                               project_id=project_id)
        else:
            d['url'] = url_for('services.client_profile', client_id=r.id, project_id=project_id)
        data.append(d)
    return jsonify({'data': data,
                    'recordsFiltered': total_filtered,
                    'recordsTotal': records_total,
                    'draw': request.args.get('draw', type=int),
                    })


@services.route('/api/projects/<int:project_id>/clients')
@services.route('/api/projects/<int:project_id>/tests/<int:test_id>')
@login_required
def get_client_list(project_id, test_id=None):
    query = Client.query.filter_by(project_id=project_id)
    records_total = query.count()
    search = request.args.get('search[value]')
    query = query.filter(or_(Client.client_number.ilike('%{}%'.format(search)),
                             Client.firstname.ilike('%{}%'.format(search)),
                             Client.lastname.ilike('%{}%'.format(search)),
                             Client.pid.ilike('%{}%'.format(search)),
                             Client.address.has(name=search),
                             ),
                         )
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    total_filtered = query.count()
    query = query.offset(start).limit(length)
    data = []
    for r in query:
        d = r.to_dict()
        if test_id:
            d['url'] = url_for('services.add_test_record',
                               client_id=r.id,
                               project_id=project_id,
                               test_id=test_id)
        elif request.args.get('for') == 'physical-exam':
            d['url'] = url_for('services.add_physical_exam_profile',
                               client_id=r.id,
                               project_id=project_id)
        elif request.args.get('for') == 'health-record':
            d['url'] = url_for('services.add_health_record',
                               client_id=r.id,
                               project_id=project_id)
        else:
            d['url'] = url_for('services.client_profile', client_id=r.id, project_id=project_id)
        data.append(d)
    return jsonify({'data': data,
                    'recordsFiltered': total_filtered,
                    'recordsTotal': records_total,
                    'draw': request.args.get('draw', type=int),
                    })


@services.route('/projects/<int:project_id>/clients/physical-exam')
@login_required
def physical_exam_profile_main(project_id):
    client_number = request.args.get('client_number')
    if client_number:
        client = Client.query.filter_by(client_number=client_number).first()
        if client:
            return redirect(url_for('services.add_physical_exam_profile', client_id=client.id, project_id=project_id))
    return render_template('services/clients/physical_exam_profile_main.html', project_id=project_id)


@services.route('/projects/<int:project_id>/clients/<int:client_id>/physical-exam', methods=['GET', 'POST'])
@login_required
def add_physical_exam_profile(client_id, project_id):
    client = Client.query.get(client_id)
    if not client:
        flash('Client not found', 'danger')
        return redirect(url_for('services.physical_exam_profile'))

    form = ClientPhysicalProfileForm()
    if form.validate_on_submit():
        pp = ClientPhysicalProfile()
        form.populate_obj(pp)
        pp.client = client
        pp.updated_by = current_user
        db.session.add(pp)
        db.session.commit()
        flash('New data have been saved.', 'success')
        return redirect(request.args.get('next') or url_for('services.physical_exam_profile_main', project_id=project_id))
    return render_template('services/clients/physical_exam_form.html', form=form, client=client, project_id=project_id)


@services.route('/projects/<int:project_id>/clients/physical-exam/<int:rec_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_physical_exam_profile(project_id, rec_id):
    rec = ClientPhysicalProfile.query.get(rec_id)
    form = ClientPhysicalProfileForm(obj=rec)
    if form.validate_on_submit():
        form.populate_obj(rec)
        rec.updated_by = current_user
        db.session.add(rec)
        db.session.commit()
        flash('Data have been updated.', 'success')
        return redirect(request.args.get('next') or
                        url_for('services.add_physical_exam_profile',
                                project_id=project_id,
                                client_id=rec.client.id,
                                ))
    return render_template('services/clients/physical_exam_form.html',
                           project_id=project_id,
                           form=form,
                           client=rec.client,
                           editing=True)


@services.route('/projects/<int:project_id>/clients/physical-exam/<int:rec_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_physical_exam_profile(project_id, rec_id):
    rec = ClientPhysicalProfile.query.get(rec_id)
    client = rec.client
    if rec:
        db.session.delete(rec)
        db.session.commit()
        flash('Data have been removed.', 'success')
    else:
        flash('The record was not found.', 'danger')
    return redirect(url_for('services.add_physical_exam_profile', client_id=client.id, project_id=project_id))


@services.route('/projects/<int:project_id>/clients/<int:client_id>/profile')
@login_required
def client_profile(client_id, project_id):
    tab = request.args.get('tab', 'stool')
    client = Client.query.get(client_id)
    return render_template('services/clients/profile.html', client=client, tab=tab, project_id=project_id)


@services.route('/projects/<int:project_id>/tests')
@login_required
def list_tests(project_id):
    tests = Test.query.all()
    profiles = TestProfile.query.all()
    return render_template('services/tests/list.html',
                           tests=tests,
                           project_id=project_id,
                           profiles=profiles)


@services.route('/projects/<int:project_id>/tests/register', methods=['POST', 'GET'])
@login_required
def register_test(project_id):
    form = TestForm()
    if form.validate_on_submit():
        test = Test()
        form.populate_obj(test)
        db.session.add(test)
        db.session.commit()
        flash('New test has been added.', 'success')
        return redirect(url_for('services.list_tests', project_id=project_id))
    else:
        for field in form.errors:
            flash(f'{field}: {form.errors[field]}', 'danger')
    return render_template('services/tests/register.html', form=form, project_id=project_id)


@services.route('/projects/<int:project_id>/tests/<int:test_id>/edit', methods=['POST', 'GET'])
@login_required
def edit_test(test_id, project_id):
    test = Test.query.get(test_id)
    form = TestForm(obj=test)
    if form.validate_on_submit():
        form.populate_obj(test)
        db.session.add(test)
        db.session.commit()
        flash('Test has been updated.', 'success')
        return redirect(url_for('services.list_tests', project_id=project_id))
    return render_template('services/tests/register.html', form=form, project_id=project_id)


@services.route('/projects/<int:project_id>/tests/<int:test_id>/records')
@login_required
def test_record_main(test_id, project_id):
    client_number = request.args.get('client_number')
    client = Client.query.filter_by(client_number=client_number).first()
    test = Test.query.get(test_id)
    if client:
        return redirect(url_for('services.add_test_record',
                                test_id=test_id,
                                client_id=client.id,
                                project_id=project_id))
    # flash('Client number not found', 'danger')
    return render_template('services/tests/main.html', project_id=project_id, test=test)


@services.route('/projects/<int:project_id>/profiles/<int:profile_id>/records')
@login_required
def test_profile_record_main(profile_id, project_id):
    test_profile = TestProfile.query.get(profile_id)
    return render_template('services/tests/profile_main.html',
                           project_id=project_id, test_profile=test_profile)


@services.route('/projects/<int:project_id>/clients/<int:client_id>/tests/<int:test_id>/records/<int:record_id>/edit',
                methods=['GET', 'POST'])
@services.route('/projects/<int:project_id>/clients/<int:client_id>/tests/<int:test_id>/records/add',
                methods=['GET', 'POST'])
@login_required
def add_test_record(project_id, test_id, client_id, record_id=None, profile_id=None):
    client = Client.query.get(client_id)
    test = Test.query.get(test_id)
    if record_id:
        rec = TestRecord.query.get(record_id)
        form = TestRecordForm(obj=rec, results=rec.value)
    else:
        rec = None
        form = TestRecordForm()
    if test.result_choices:
        form.results.choices = [(c, c) for c in test.result_choices.split(',')]
    else:
        form.results.choices = []
    if request.method == 'POST':
        if form.validate_on_submit():
            if not record_id:
                rec = TestRecord()
            form.populate_obj(rec)
            if test.result_choices:
                rec.value = form.results.data
            rec.test = test
            rec.updated_by = current_user
            rec.client_id = client_id
            db.session.add(rec)
            db.session.commit()
            flash('Test has been updated.', 'success')
            if request.args.get('next'):
                return redirect(request.args.get('next'))
            else:
                return redirect(url_for('services.add_test_record',
                                        client_id=client_id, test_id=test_id, project_id=project_id))
        else:
            flash(f'{form.errors}', 'light')
    return render_template('services/tests/record_form.html',
                           form=form,
                           test=test,
                           project_id=project_id,
                           record=rec,
                           record_id=record_id,
                           client=client)


@services.route('/projects/<int:project_id>/clients/<int:client_id>/profiles/<int:profile_id>/records/add',
                methods=['GEt', 'POST'])
@login_required
def add_test_profile_record(project_id, client_id, profile_id):
    client = Client.query.get(client_id)
    test_profile = TestProfile.query.get(profile_id)
    form = create_test_profile_record_form(test_profile)()
    for test in test_profile.tests:
        _form = getattr(form, test.name)
        if request.method == 'GET':
            test_record = TestRecord.query.filter_by(test=test, client_id=client_id).first()
            if test_record:
                _form.value.process_data(test_record.value)
                _form.results.process_data(test_record.value)
        if test.result_choices:
            _form.results.choices = [(c, c) for c in test.result_choices.split(',')]
        else:
            _form.results.choices = []
    if form.validate_on_submit():
        print(form.data)
        for test in test_profile.tests:
            _form = getattr(form, test.name)
            test_record = TestRecord.query.filter_by(test=test, client_id=client_id).first()
            if not test_record:
                test_record = TestRecord(test=test, client_id=client_id)
            if test.result_choices:
                test_record.value = _form.results.data
            else:
                print(f'Old value={test_record.value}, new value={_form.value.data}')
                test_record.value = _form.value.data
            test_record.updated_at = arrow.now('Asia/Bangkok').datetime
            db.session.add(test_record)
            db.session.commit()
        return redirect(url_for('services.test_profile_record_main', profile_id=test_profile.id, project_id=project_id))
    if form.errors:
        flash(f'{form.errors}', 'danger')
    return render_template('services/tests/profile_record_form.html',
                           form=form,
                           test_profile=test_profile,
                           project_id=project_id,
                           client=client)


@services.route('/projects/<int:project_id>/clients/<int:client_id>/tests/<int:test_id>/records/<int:record_id>/delete',
                methods=['GET', 'POST'])
@login_required
def delete_test_record(project_id, test_id, client_id, record_id):
    client = Client.query.get(client_id)
    test = Test.query.get(test_id)
    rec = TestRecord.query.get(record_id)
    if rec:
        db.session.delete(rec)
        db.session.commit()
        flash('The record has been deleted.', 'success')
    else:
        flash('The record was not found.', 'danger')
    return redirect(url_for('services.add_test_record',
                            project_id=project_id,
                            test_id=test_id,
                            client_id=client_id))


@services.route('/projects/<int:project_id>/stool-exam')
@services.route('/clients/<int:client_id>/stool-exam')
@login_required
def stool_exam_main(client_id=None, project_id=None):
    lab_number = request.args.get('lab_number')
    collection_datetime = request.args.get('collection_datetime')
    if collection_datetime:
        collection_datetime = datetime.strptime(collection_datetime, '%Y-%m-%d %H:%M:%S')
        collection_datetime = collection_datetime.astimezone(timezone('Etc/UTC'))

    next_url = request.args.get('next')
    if not client_id:
        client_id = request.args.get('client_id')
    if lab_number:
        record = StoolTestRecord.query.filter_by(lab_number=lab_number).first()
        if not record:
            if client_id:
                record = StoolTestRecord(lab_number=lab_number, collection_datetime=collection_datetime)
                record.client_id = client_id
                record.updated_by = current_user
                db.session.add(record)
                db.session.commit()
                flash('New stool specimens has been registered.', 'success')
                return redirect(next_url)
            else:
                flash('The lab number was not registered.', 'danger')
                if next_url:
                    return redirect(next_url)
        else:
            flash('The lab number is already registered.', 'warning')
            return redirect(next_url or url_for('services.edit_stool_exam_record', record_id=record.id))
    records = StoolTestRecord.query.filter(StoolTestRecord.client.has(project_id=project_id))
    client = Client.query.get(client_id)
    return render_template('services/clients/stool_exam_main.html',
                           records=records,
                           project_id=project_id or client.project_id)


@services.route('/api/projects/<int:project_id>/stool-exam/records')
@login_required
def get_stool_exam_records(project_id):
    # TODO: add pagination
    records = [rec.to_dict() for rec in StoolTestRecord.query.filter(StoolTestRecord.client.has(project_id=project_id))]
    return jsonify({'data': records})


@services.route('/stool-exam/records/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_stool_exam_record(record_id):
    # TODO: Use Select2js for the organism field
    not_found_org = Organism.query.filter_by(name='Not found').first()
    not_found_stage = Stage.query.filter_by(stage='Not found').first()
    record = StoolTestRecord.query.get(record_id)
    form = StoolTestForm(obj=record)
    if form.validate_on_submit():
        form.populate_obj(record)
        if form.not_found.data == 'Not found':
            record.items = [StoolTestReportItem(organism=not_found_org,
                                                stage=not_found_stage)]
        record.updated_by = current_user
        db.session.add(record)
        db.session.commit()
        flash('Data have been saved.', 'success')
    else:
        for field in form.errors:
            flash(f'{field} {form.errors[field]}', 'danger')
    if len(record.items) == 1 and record.items[0].organism == not_found_org:
        form.not_found.data = 'Not found'
    elif len(record.items) == 0:
        form.not_found.data = 'Not found'
    else:
        form.not_found.data = 'Found'

    # client_body = [
    #     ["ชื่อ", record.client.fullname or '-', 'รหัส', record.client.client_number, "เพศ", record.client.gender or '-'],
    #     ['อายุ', record.client.age if record.client.age_ or record.client.dob else '-', 'หมายเลขบัตรประชาชน', record.client.pid if not record.client.pid.startswith('fake') else '-'],
    # ]
    client_body = [
        ["ชื่อ", record.client.fullname or '-', 'รหัส', record.client.client_number],
        ['อายุ', record.client.age if record.client.age_ or record.client.dob else '-', 'หมายเลขบัตรประชาชน', record.client.pid if not record.client.pid.startswith('fake') else '-'],
    ]
    macro_stool_records = []
    occult_blood = []
    stool_records = [
        ['ลำดับ', 'ชื่อปรสิต', 'ระยะ', 'หมายเหตุ', '']
    ]
    if record.reported_at:
        if record.color != 'ไม่ได้ส่งอุจจาระ' or record.form != 'ไม่ได้ส่งอุจจาระ':
            macro_stool_records.append([
                'สี', record.color or '-', 'ลักษณะ', record.form or '-', ''
            ])
        if record.occult_blood is True:
            occult_blood_interpret = 'พบเลือดแฝงในอุจจาระ'
            occult_blood_result = 'ผลบวก'
        elif record.occult_blood is False:
            occult_blood_interpret = 'ไม่พบเลือดแฝงในอุจจาระ'
            occult_blood_result = 'ผลลบ'
        else:
            occult_blood_interpret = ''
            occult_blood_result = 'ไม่ได้ทดสอบ'
        occult_blood.append([
            occult_blood_result, occult_blood_interpret, ''
        ])
        for n, item in enumerate(record.items, start=1):
            if item.organism.name == 'Not found':
                stool_records.append([
                    n, 'ไม่พบปรสิต', '', '', ''
                ])
            else:
                stool_records.append([
                    n, item.organism.name, item.stage.stage,
                    item.comment or '...........................................................', ''
                ])
    # if not macro_stool_records:
    #     macro_stool_records.append(['สี', '-', 'ลักษณะ', '-', ''])
    # if not occult_blood:
    #     occult_blood.append(['ไม่ได้ทดสอบ', '', ''])
    # if len(stool_records) == 1:
    #     stool_records.pop()
    #     stool_records.append(['', 'ไม่ได้ทดสอบ', '', '', ''])
    return render_template('services/clients/stool_exam_form.html',
                           form=form,
                           record=record,
                           client=record.client,
                           client_body=client_body,
                           stool_records=stool_records,
                           macro_stool_records=macro_stool_records,
                           occult_blood=occult_blood,
                           summary=record.summary,
                           reported_date=arrow.now('Asia/Bangkok').datetime.strftime('%d/%m/%Y'),
                           next_url=request.args.get('next'))


@services.route('/stool-exam/records/<int:record_id>/report', methods=['GET', 'POST'])
@login_required
def report_stool_exam_record(record_id):
    record = StoolTestRecord.query.get(record_id)
    if record:
        record.reported_at = arrow.now('Asia/Bangkok').datetime
        record.reported_by = current_user
        db.session.add(record)
        db.session.commit()
        flash('The record have been reported.', 'success')
    else:
        flash('The record was not found.', 'danger')
    return redirect(request.args.get('next')
                    or url_for('services.stool_exam_main',
                               project_id=record.client.project_id))


@services.route('/stool-exam/records/<int:record_id>/approve-report')
@superuser
@login_required
def approve_report_stool_exam_record(record_id):
    record = StoolTestRecord.query.get(record_id)
    project_id = record.client.project_id
    if record and current_user.license_id:
        record.approved_at = arrow.now('Asia/Bangkok').datetime
        record.approved_by = current_user
        db.session.add(record)
        db.session.commit()
        flash('The report has been approved.', 'success')
    else:
        flash('The record has not been approved.', 'danger')
    return redirect(request.args.get('next')
                    or url_for('services.stool_exam_main',
                               project_id=project_id
                               )
                    )


@services.route('/stool-exam/records/<int:record_id>/cancel-report', methods=['GET', 'POST'])
@superuser
@login_required
def cancel_report_stool_exam_record(record_id):
    record = StoolTestRecord.query.get(record_id)
    project_id = record.client.project_id
    if record:
        record.reported_at = None
        record.reported_by = None
        db.session.add(record)
        db.session.commit()
        flash('The report has been cancelled.', 'success')
    else:
        flash('The record was not found.', 'danger')
    return redirect(request.args.get('next')
                    or url_for('services.stool_exam_main',
                               project_id=project_id
                               )
                    )


@services.route('/stool-exam/records/<int:record_id>/remove', methods=['GET', 'POST'])
@login_required
def remove_stool_exam_record(record_id):
    record = StoolTestRecord.query.get(record_id)
    if record:
        client = record.client
        db.session.delete(record)
        db.session.commit()
        flash('The record have been removed.', 'success')
    else:
        flash('The record was not found.', 'danger')
        return redirect(url_for('services.stool_exam_main'))
    return redirect(url_for('services.stool_exam_main', client_id=client.id))


@services.route('/add-report-item-entry', methods=['POST'])
@login_required
def add_stool_report_item_entry():
    form = StoolTestForm()
    form.items.append_entry()
    item_form = form.items[-1]
    return f'''
          <div class="box">
            {item_form.hidden_tag()}
            <div class="field">
              <label class="label">{item_form.organism.label}</label>
              <div class="select">
                {item_form.organism()}
              </div>
            </div>
            <div class="field">
              <label class="label">{item_form.stage.label}</label>
              <div class="select">
                {item_form.stage()}
              </div>
            </div>
            <div class="field">
              <label class="label">{item_form.comment.label}</label>
              <div class="control">
                {item_form.comment(class_='textarea')}
              </div>
            </div>
          </div>
          '''


@services.route('/remove-report-item-entry', methods=['POST'])
@login_required
def remove_stool_report_item_entry():
    form = StoolTestForm()
    if len(form.items.entries) > 1:
        entry_ = form.items.pop_entry()
    content = ''
    for item_form in form.items.entries:
        content += f'''
              <div class="box">
                {item_form.hidden_tag()}
                <div class="field">
                  <label class="label">{item_form.organism.label}</label>
                  <div class="select">
                    {item_form.organism()}
                  </div>
                </div>
                <div class="field">
                  <label class="label">{item_form.stage.label}</label>
                  <div class="select">
                    {item_form.stage()}
                  </div>
                </div>
              </div>
              '''
    if len(form.items.entries) == 1:
        content += '''<span class="has-text-danger">
                At least one report item is needed.
                </span>
            '''
    resp = make_response(content)
    return resp


@services.route('/projects/<int:project_id>/health_records')
@login_required
def health_record_main(project_id):
    client_number = request.args.get('client_number')
    if client_number:
        client = Client.query.filter_by(client_number=client_number).first()
        if client:
            return redirect(url_for('services.add_health_record', client_id=client.id, project_id=project_id))
    return render_template('services/clients/health_record_main.html', project_id=project_id)


@services.route('/projects/<int:project_id>/clients/<int:client_id>/health-record', methods=['GET', 'POST'])
@services.route('/projects/<int:project_id>/clients/<int:client_id>/health-record/<int:record_id>', methods=['GET', 'POST'])
@login_required
def add_health_record(project_id, client_id, record_id=None):
    if record_id:
        record = HealthRecord.query.get(record_id)
        form = HealthRecordForm(obj=record)
    else:
        form = HealthRecordForm()
    client = Client.query.get(client_id)
    if form.validate_on_submit():
        if not record_id:
            record = HealthRecord()
            record.client_id = client_id
        form.populate_obj(record)
        record.updated_by = current_user
        db.session.add(record)
        db.session.commit()
        flash('Data have been saved.', 'success')
        if request.args.get('next'):
            return redirect(request.args.get('next'))
    return render_template('services/clients/health_record_form.html',
                           form=form, client=client, project_id=project_id)


@services.route('/projects/<int:project_id>/clients/<int:client_id>/health-record/<int:record_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_health_record(project_id, client_id, record_id):
    if record_id:
        record = HealthRecord.query.get(record_id)
        db.session.delete(record)
        db.session.commit()
        flash('The record has been deleted.', 'success')
    else:
        flash('The record was not found.', 'danger')
    return redirect(url_for('services.add_health_record', client_id=client_id, project_id=project_id))


@services.route('/tests/<int:test_id>/delete')
@login_required
def delete_test(test_id):
    test = Test.query.get(test_id)
    if test:
        db.session.delete(test)
        db.session.commit()
        flash('Test has been removed.', 'success')
    else:
        flash('The test was not found.', 'danger')
    return redirect(url_for('services.list_tests'))


@services.route('/projects/<int:project_id>/clients/<int:client_id>/report-preview')
@login_required
def preview_report(project_id, client_id):
    client = Client.query.get(client_id)
    project = Project.query.get(project_id)
    client_pid = '-' if client.pid.startswith('fake') else client.pid
    client_body = [
        ["ชื่อ", client.fullname or '-', "เพศ", client.gender or '-', ''],
        ['อายุ', client.age, 'หมายเลขบัตรประชาชน', client_pid, ''],
    ]
    physical_exam = []
    for rec in client.physical_profiles:
        physical_exam.append(['น้ำหนัก (กก.)', rec.weight, 'ส่วนสูง (ซม.)', rec.height, 'รอบเอว (ซม.)', rec.waist, ''])
        physical_exam.append(
            ['ดัชนีมวลกาย', rec.bmi, f'({rec.get_bmi_interpretation()})', 'ความดันโลหิต', rec.bp, "", ''])
    if not physical_exam:
        physical_exam.append(['น้ำหนัก (กก.)', '-', 'ส่วนสูง (ซม.)', '-', 'รอบเอว (ซม.)', '-', ''])
        physical_exam.append(['ดัชนีมวลกาย', '-', '', 'ความดันโลหิต', '-', '', ''])

    underlying_diseases = []
    for rec in client.health_records:
        underlying_diseases.append([f"อดอาหารมา {rec.fasting_time} ชม.", ""])
        for n, d in enumerate(rec.underlying_diseases, start=1):
            underlying_diseases.append([f'{n}.{d.name}', ''])
    if not underlying_diseases:
        underlying_diseases.append(['ไม่มี', ''])

    family_diseases = []
    for rec in client.health_records:
        for n, d in enumerate(rec.family_diseases, start=1):
            family_diseases.append([f'{n}.{d.name}', ''])
    if not family_diseases:
        family_diseases.append(['ไม่มี', ''])
    test_records = [
        ['รายการทดสอบ', 'ค่าการทดสอบ', 'หน่วย', 'แปลผล', 'ค่าอ้างอิง', '']
    ]
    if client.test_records:
        for rec in client.test_records:
            test_records.append([rec.test.name, rec.value, rec.test.unit, f'({rec.interpret})',
                                 f'{rec.test.reference} ({rec.test.unit})', ''])
    if len(test_records) == 1:
        test_records.append(["", "", "", "", "", ""])

    stool_records = [
        ['ลำดับ', 'ชื่อปรสิต', 'ระยะ', 'หมายเหตุ', '']
    ]
    macro_stool_records = []
    occult_blood = []
    for rec in client.stool_exam_records:
        if rec.reported_at:
            macro_stool_records.append([
                'สี', rec.color or '-', 'ลักษณะ', rec.form or '-', ''
            ])
            if rec.occult_blood is True:
                occult_blood_interpret = 'พบเลือดแฝงในอุจจาระ'
                occult_blood_result = 'ผลบวก'
            elif rec.occult_blood is False:
                occult_blood_interpret = 'ไม่พบเลือดแฝงในอุจจาระ'
                occult_blood_result = 'ผลลบ'
            else:
                occult_blood_interpret = ''
                occult_blood_result = 'ไม่ได้ทดสอบ'
            occult_blood.append([
                occult_blood_result, occult_blood_interpret, ''
            ])
            for n, item in enumerate(rec.items, start=1):
                if item.organism.name == 'Not found':
                    stool_records.append([
                        n, 'ไม่พบปรสิต', '', '', ''
                    ])
                else:
                    stool_records.append([
                        n, item.organism.name, item.stage.stage,
                        '...........................................................', ''
                    ])
    if not macro_stool_records:
        macro_stool_records.append(['สี', '-', 'ลักษณะ', '-', ''])
    if not occult_blood:
        occult_blood.append(['ไม่ได้ทดสอบ', '', ''])
    if len(stool_records) == 1:
        stool_records.pop()
        stool_records.append(['', 'ไม่ได้ทดสอบ', '', '', ''])

    return render_template('services/clients/report_preview.html',
                           client=client,
                           project=project,
                           client_body=client_body,
                           physical_body=physical_exam,
                           underlying_diseases=underlying_diseases,
                           family_diseases=family_diseases,
                           test_records=test_records,
                           stool_records=stool_records,
                           macro_stool_records=macro_stool_records,
                           occult_blood=occult_blood,
                           reported_date=arrow.now('Asia/Bangkok').datetime.strftime('%d/%m/%Y')
                           )


@services.route('/api/projects/<int:project_id>/stool/statistics')
def get_stool_exam_statistics(project_id):
    desc = [('name', 'string'), ('cases', 'number')]
    data_dict = defaultdict(int)
    for report in StoolTestReportItem.query.all():
        if report.record.client.project_id == project_id:
            data_dict[report.organism.name] += 1

    data = [[name, data_dict[name]] for name in data_dict]
    data_table = gviz_api.DataTable(desc)
    data_table.LoadData(data)
    json = data_table.ToJSon()
    return json


@services.route('/api/<int:project_id>/stool/statistics/address')
def get_stool_exam_statistics_address(project_id):
    desc = [('name', 'string'), ('cases', 'number')]
    data_dict = defaultdict(int)
    for rec in StoolTestRecord.query.all():
        if rec.client.project_id == project_id:
            if not rec.client:
                continue
            if rec.client.address:
                data_dict[rec.client.address.name] += 1
            else:
                data_dict['N/A'] += 1

    data = [[name, data_dict[name]] for name in data_dict]
    data_table = gviz_api.DataTable(desc)
    data_table.LoadData(data)
    json = data_table.ToJSon()
    return json


@services.route('/api/<int:project_id>/stool/statistics/processed')
def get_stool_exam_statistics_processed(project_id):
    desc = [('name', 'string'), ('numbers', 'number')]
    data_dict = defaultdict(int)
    for rec in StoolTestRecord.query.all():
        if rec.client.project_id == project_id:
            if rec.reported_at:
                data_dict['reported'] += 1
            else:
                data_dict['waiting'] += 1

    data = [[name, data_dict[name]] for name in data_dict]
    data_table = gviz_api.DataTable(desc)
    data_table.LoadData(data)
    json = data_table.ToJSon()
    return json
