from os import environ

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.key import secret_key

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = environ['SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = secret_key()

    __import__("app.models")
    db.init_app(app=app)
    migrate.init_app(app=app, db=db)

    from . import views
    for view in [getattr(views, x) for x in views.__all__]:
        app.register_blueprint(blueprint=view.bp)

    from . import template_filter
    app.add_template_filter(template_filter.date_to_string)
    app.add_template_filter(template_filter.parse_user_agent)
    app.add_template_filter(template_filter.to_html)
    app.add_template_filter(template_filter.parse_options)
    app.add_template_filter(template_filter.type_to_string)

    return app
