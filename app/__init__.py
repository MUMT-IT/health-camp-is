import os

import arrow
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate

load_dotenv()

db = SQLAlchemy()
migrate = Migrate(db=db)
admin = Admin()
login_manager = LoginManager()


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    database_url = os.environ.get('DATABASE_URL')
    if not database_url.startswith('postgresql'):
        database_url = database_url.replace('postgres', 'postgresql')
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=database_url,
    )

    db.init_app(app)
    migrate.init_app(app)
    admin.init_app(app)
    login_manager.init_app(app)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.services import service_bp
    app.register_blueprint(service_bp)
    from app.services.models import (Client, Test, TestRecord, StoolTestRecord,
                                     StoolTestReportItem, Organism, Stage, User,
                                     UnderlyingDisease, FamilyDiseases)

    admin.add_view(ModelView(Client, db.session, category='Client'))
    admin.add_view(ModelView(Test, db.session, category='Test'))
    admin.add_view(ModelView(TestRecord, db.session, category='Test'))
    admin.add_view(ModelView(StoolTestRecord, db.session, category='Stool'))
    admin.add_view(ModelView(StoolTestReportItem, db.session, category='Stool'))
    admin.add_view(ModelView(Organism, db.session, category='Stool'))
    admin.add_view(ModelView(Stage, db.session, category='Stool'))
    admin.add_view(ModelView(UnderlyingDisease, db.session, category='Diseases'))
    admin.add_view(ModelView(FamilyDiseases, db.session, category='Diseases'))
    admin.add_view(ModelView(User, db.session, category='Users'))

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.template_filter('localdatetime')
    def get_local_datetime(dt):
        if dt:
            d = arrow.get(dt, 'Asia/Bangkok')
            return f'{d.format("DD/MM/YYYY HH:mm:ss")} ({d.humanize()})'
        return ''

    @app.template_filter('itemize')
    def itemize(text, delimiter='<br>'):
        return text.replace(',', delimiter)

    return app
