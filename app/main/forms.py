from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired


class NoteForm(FlaskForm):
    note = TextAreaField("Just write here", validators=[DataRequired()])
    submit = SubmitField("Submit")
