import os
from flask import Flask
from config import config_select
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate
from flask_login import LoginManager


class Base(DeclarativeBase):
    pass


database = SQLAlchemy(model_class=Base)
migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "You need to authenticate"


def create_app(config_name="default"):
    # create the app
    application = Flask(__name__,
                        instance_relative_config=True)

    # configure the app
    application.config.from_object(config_select[config_name])
    if config_name == "production":
        application.config.from_pyfile("prod_conf.py", silent=True)
    elif config_name in ["dev", "default"]:
        application.config.from_mapping(
            SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(application.instance_path,
                                                                "homenotes-db-dev.sqlite")
        )

    # ensure the instance folder exists
    os.makedirs(application.instance_path, exist_ok=True)

    # extensions initialization
    database.init_app(application)
    migrate.init_app(application, database)
    login_manager.init_app(application)

    # blueprints registration
    from app.auth import bp as auth_bp
    application.register_blueprint(auth_bp)
    from app.main import bp as main_bp
    application.register_blueprint(main_bp)

    # add simple page that says hello
    @application.route("/hello")
    def hello():
        return "Hello!"

    return application


from app import models
