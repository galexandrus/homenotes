from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, EqualTo
import sqlalchemy as sa
from app import database
from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Enter your name", validators=[DataRequired()])
    passwd = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Log in")


class RegistrationForm(FlaskForm):
    username = StringField("Enter your name", validators=[DataRequired()])
    email = StringField("Enter your email", validators=[DataRequired()])
    passwd = PasswordField("Password", validators=[DataRequired()])
    passwd2 = PasswordField("Repeat password", validators=[DataRequired(),
                                                           EqualTo("passwd")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = database.session.scalar(
            sa.select(User).where(User.name == username.data)
        )
        if user is not None:
            raise ValidationError("A user with that name already exists")

    def validate_email(self, email):
        user = database.session.scalar(
            sa.select(User).where(User.email == email.data)
        )
        if user is not None:
            raise ValidationError("A user with that email address already exists")
