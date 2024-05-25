import os
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, database
from app.models import Role, User, Note


application = create_app(os.getenv("HOMENOTES_CONFIG"))


@application.shell_context_processor
def make_shell_context():
    return {
        "sa": sa,
        "so": so,
        "db": database,
        "Role": Role,
        "User": User,
        "Note": Note
    }
