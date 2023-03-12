import os

import arrow
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

load_dotenv()

db = SQLAlchemy()
migrate = Migrate(db=db)


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL'),
    )

    db.init_app(app)
    migrate.init_app(app)

    from app.services import service_bp
    app.register_blueprint(service_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.template_filter('localdatetime')
    def get_local_datetime(dt):
        if dt:
            d = arrow.get(dt, 'Asia/Bangkok')
            return f'{d.format("DD/MM/YYYY HH:mm:ss")} ({d.humanize()})'
        return ''

    return app
